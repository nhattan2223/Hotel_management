"""Test service layer business logic."""
import datetime
import os
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from database.schema import create_tables
from database.seed_data import seed_all


@pytest.fixture
def patched_db():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_tables(conn)
    seed_all(conn)
    conn.close()

    import models.base_model
    with patch.object(models.base_model, "DB_PATH", db_path):
        yield db_path

    os.close(db_fd)
    os.unlink(db_path)


class TestComputeRoomDisplayStatus:
    def test_dirty_room(self, patched_db):
        from services.booking_service import compute_room_display_status
        from utils.config import STATUS_DIRTY
        room = {"housekeeping": STATUS_DIRTY, "occupancy_status": "Available", "id": 999}
        assert compute_room_display_status(room) == STATUS_DIRTY

    def test_occupied_room(self, patched_db):
        from services.booking_service import compute_room_display_status
        from utils.config import STATUS_OCCUPIED
        room = {"housekeeping": "Clean", "occupancy_status": STATUS_OCCUPIED, "id": 999}
        assert compute_room_display_status(room) == STATUS_OCCUPIED

    def test_available_room(self, patched_db):
        from services.booking_service import compute_room_display_status
        from utils.config import STATUS_AVAILABLE
        room = {"housekeeping": "Clean", "occupancy_status": STATUS_AVAILABLE, "id": 999}
        assert compute_room_display_status(room) == STATUS_AVAILABLE


class TestBookingValidation:
    def test_is_checkin_time_reached(self):
        from services.booking_service import is_checkin_time_reached
        future = datetime.datetime(2099, 1, 1, 14, 0)
        booking = {"check_in_date": "2099-01-01T14:00:00"}
        assert not is_checkin_time_reached(booking, now=datetime.datetime(2099, 1, 1, 12, 0))
        assert is_checkin_time_reached(booking, now=datetime.datetime(2099, 1, 1, 14, 0))
        assert is_checkin_time_reached(booking, now=datetime.datetime(2099, 1, 1, 15, 0))

    def test_format_booking_datetime(self):
        from services.booking_service import format_booking_datetime
        result = format_booking_datetime("2026-06-15T14:30:00")
        assert result == "15/06/2026 14:30"

    def test_create_booking_invalid_dates(self, patched_db):
        from services.booking_service import create_booking_with_validation
        result = create_booking_with_validation(
            1, [1], 1, "invalid-date", "2026-06-03T12:00:00", 0, ""
        )
        assert not result["ok"]

        result = create_booking_with_validation(
            1, [1], 1, "2026-06-05T14:00:00", "2026-06-03T12:00:00", 0, ""
        )
        assert not result["ok"]
        assert "sau" in result["error"]

    def test_create_booking_deposit_too_high(self, patched_db):
        from services.booking_service import create_booking_with_validation
        result = create_booking_with_validation(
            1, [1], 1, "2026-06-01T14:00:00", "2026-06-03T12:00:00", 99_000_000, ""
        )
        assert not result["ok"]
        assert "đặt cọc" in result["error"].lower()


class TestInvoiceComputation:
    def test_compute_invoice_no_booking(self, patched_db):
        from services.booking_service import compute_invoice
        assert compute_invoice(9999) == {}

    def test_cancel_expired_unchecked(self, patched_db):
        from services.booking_service import cancel_expired_unchecked_bookings
        now = datetime.datetime(2020, 1, 1)
        count = cancel_expired_unchecked_bookings(now=now)
        assert count >= 0

    def test_checkout_expired_checkedin(self, patched_db):
        from services.booking_service import checkout_expired_checkedin_bookings
        now = datetime.datetime(2020, 1, 1)
        count = checkout_expired_checkedin_bookings(now=now)
        assert count >= 0


class TestSwitchRoom:
    def test_switch_room_no_booking(self, patched_db):
        from services.booking_service import switch_room
        result = switch_room(9999, 1, 2, "2026-06-02T12:00:00")
        assert not result["ok"]
        assert "Không tìm thấy" in result["error"]


class TestServiceModelIntegration:
    def test_service_crud(self, patched_db):
        from models import service_model
        svcs = service_model.get_services(active_only=False)
        assert len(svcs) >= 7

        svc = service_model.get_service(1)
        assert svc is not None

        service_model.create_service(None, "Test Service", 100000)
        svcs = service_model.get_services(active_only=False)
        assert any(s["service_name"] == "Test Service" for s in svcs)

        service_model.update_service(1, None, "Updated Service", 150000, 1)
        updated = service_model.get_service(1)
        assert updated["service_name"] == "Updated Service"


class TestMenuModelIntegration:
    def test_meal_types(self, patched_db):
        from models import menu_model
        types = menu_model.get_meal_types()
        assert len(types) >= 4

    def test_menu_items(self, patched_db):
        from models import menu_model
        items = menu_model.get_menu_items(active_only=False)
        assert len(items) >= 9

    def test_create_menu_item(self, patched_db):
        from models import menu_model
        menu_model.create_menu_item(1, "Test Dish", 75000)
        items = menu_model.get_menu_items(active_only=False)
        assert any(i["item_name"] == "Test Dish" for i in items)


class TestInvoiceModelIntegration:
    def test_create_invoice(self, patched_db):
        from models import customer_model, booking_model, invoice_model
        from utils.config import BOOKING_CHECKED_OUT

        cid = customer_model.create_customer("Invoice Test", None, None, None, None)
        bid = booking_model.create_booking(cid, 1, "2026-05-01T14:00:00", "2026-05-03T12:00:00", 100000, "")
        booking_model.checkin_booking(bid)
        booking_model.checkout_booking(bid, 1)

        from utils.config import PAYMENT_STATUS_PAID
        invoice_model.upsert_invoice(bid, 1000000, 200000, 150000, 50000, 100000, 1300000, "Cash", PAYMENT_STATUS_PAID)

        inv = invoice_model.get_invoice(bid)
        assert inv is not None
        assert inv["final_amount"] == 1300000
