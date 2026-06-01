"""Test model layer with a temporary test database."""
import os
import sqlite3
import tempfile
from unittest.mock import patch

import pytest

from database.schema import create_tables
from database.seed_data import seed_all


@pytest.fixture
def patched_db():
    """Create test DB and patch DB_PATH at the base_model level (where it's imported)."""
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


class TestHotelModel:
    def test_get_all_hotels(self, patched_db):
        from models import hotel_model
        hotels = hotel_model.get_all_hotels()
        assert len(hotels) >= 2
        names = [h["name"] for h in hotels]
        assert "Grand Palace Hotel" in names
        assert "Ocean View Resort" in names

    def test_get_hotel(self, patched_db):
        from models import hotel_model
        hotel = hotel_model.get_hotel(1)
        assert hotel is not None
        assert hotel["name"] == "Grand Palace Hotel"

    def test_get_hotel_not_found(self, patched_db):
        from models import hotel_model
        assert hotel_model.get_hotel(999) is None


class TestRoomTypeModel:
    def test_get_room_types(self, patched_db):
        from models import room_model
        types = room_model.get_room_types()
        assert len(types) >= 4
        names = [t["type_name"] for t in types]
        assert "Standard" in names
        assert "Deluxe" in names
        assert "Suite" in names

    def test_create_and_update_room_type(self, patched_db):
        from models import room_model
        room_model.create_room_type("Penthouse", 2500000, 6, "Penthouse sang trọng")
        types = room_model.get_room_types()
        assert any(t["type_name"] == "Penthouse" for t in types)

        penthouse = [t for t in types if t["type_name"] == "Penthouse"][0]
        room_model.update_room_type(penthouse["id"], "Penthouse VIP", 3000000, 4, "")
        updated = room_model.get_room_types()
        vip = [t for t in updated if t["id"] == penthouse["id"]][0]
        assert vip["type_name"] == "Penthouse VIP"
        assert vip["price_per_night"] == 3000000


class TestRoomModel:
    def test_get_rooms(self, patched_db):
        from models import room_model
        rooms = room_model.get_rooms()
        assert len(rooms) >= 20  # 13 + 13 rooms from seed

    def test_get_rooms_by_hotel(self, patched_db):
        from models import room_model
        rooms = room_model.get_rooms(hotel_id=1)
        assert len(rooms) == 13
        for r in rooms:
            assert r["hotel_id"] == 1

    def test_get_room(self, patched_db):
        from models import room_model
        room = room_model.get_room(1)
        assert room is not None
        assert "room_number" in room
        assert "type_name" in room

    def test_create_and_delete_room(self, patched_db):
        from models import room_model
        room_model.create_room(1, 1, "999", 9)
        rooms = room_model.get_rooms(hotel_id=1)
        assert any(r["room_number"] == "999" for r in rooms)

        new_room = [r for r in rooms if r["room_number"] == "999"][0]
        room_model.delete_room(new_room["id"])
        rooms_after = room_model.get_rooms(hotel_id=1)
        assert not any(r["room_number"] == "999" for r in rooms_after)

    def test_housekeeping_status(self, patched_db):
        from models import room_model
        from utils.config import STATUS_DIRTY, STATUS_CLEAN
        room_model.set_housekeeping_status(1, STATUS_DIRTY)
        room = room_model.get_room(1)
        assert room["housekeeping"] == STATUS_DIRTY

        room_model.set_housekeeping_status(1, STATUS_CLEAN)
        room = room_model.get_room(1)
        assert room["housekeeping"] == STATUS_CLEAN


class TestCustomerModel:
    def test_get_all_customers_empty(self, patched_db):
        from models import customer_model
        customers = customer_model.get_all_customers()
        assert len(customers) == 0

    def test_create_and_find_customer(self, patched_db):
        from models import customer_model
        cid = customer_model.create_customer("Nguyen Van A", "123456789012", "0901234567", "a@test.com", "HCM")
        assert cid is not None

        cust = customer_model.get_customer(cid)
        assert cust["full_name"] == "Nguyen Van A"
        assert cust["id_card"] == "123456789012"

        found = customer_model.find_by_id_card("123456789012")
        assert found is not None
        assert found["full_name"] == "Nguyen Van A"

    def test_update_customer(self, patched_db):
        from models import customer_model
        cid = customer_model.create_customer("Test User", None, None, None, None)
        customer_model.update_customer(cid, "Updated Name", "987654321098", "0999999999", "u@test.com", "HN")
        updated = customer_model.get_customer(cid)
        assert updated["full_name"] == "Updated Name"
        assert updated["id_card"] == "987654321098"

    def test_delete_customer(self, patched_db):
        from models import customer_model
        cid = customer_model.create_customer("To Delete", None, None, None, None)
        customer_model.delete_customer(cid)
        cust = customer_model.get_customer(cid)
        assert cust is not None
        assert cust["is_active"] == 0

    def test_search_customers(self, patched_db):
        from models import customer_model
        customer_model.create_customer("Alice Wonderland", "111111111111", "0900000001", None, None)
        customer_model.create_customer("Bob Marley", "222222222222", "0900000002", None, None)

        results = customer_model.search_customers("Alice")
        assert len(results) == 1
        assert results[0]["full_name"] == "Alice Wonderland"

        results = customer_model.search_customers("111111")
        assert len(results) == 1


class TestBookingModel:
    def test_create_booking_flow(self, patched_db):
        from models import customer_model, booking_model, room_model
        from utils.config import BOOKING_RESERVED, BOOKING_CHECKED_IN, BOOKING_CHECKED_OUT

        cid = customer_model.create_customer("Booking Guest", None, None, None, None)
        bid = booking_model.create_booking(cid, 1, "2026-06-01T14:00:00", "2026-06-03T12:00:00", 500000, "Test booking")

        booking_model.set_booking_rooms(bid, [{"room_id": 1, "price_snapshot": 500000}])

        bk = booking_model.get_booking(bid)
        assert bk is not None
        assert bk["status"] == BOOKING_RESERVED
        assert bk["deposit_amount"] == 500000
        rooms = booking_model.get_booking_rooms(bid)
        assert len(rooms) == 1
        assert rooms[0]["room_id"] == 1

        booking_model.checkin_booking(bid)
        bk = booking_model.get_booking(bid)
        assert bk["status"] == BOOKING_CHECKED_IN

        booking_model.checkout_booking(bid, 1)
        bk = booking_model.get_booking(bid)
        assert bk["status"] == BOOKING_CHECKED_OUT

    def test_cancel_booking(self, patched_db):
        from models import customer_model, booking_model
        from utils.config import BOOKING_CANCELLED

        cid = customer_model.create_customer("Cancel Test", None, None, None, None)
        bid = booking_model.create_booking(cid, 1, "2026-07-01T14:00:00", "2026-07-03T12:00:00", 0, "")
        booking_model.set_booking_rooms(bid, [{"room_id": 1, "price_snapshot": 500000}])
        booking_model.cancel_booking(bid)
        bk = booking_model.get_booking(bid)
        assert bk["status"] == BOOKING_CANCELLED

    def test_get_bookings(self, patched_db):
        from models import customer_model, booking_model
        cid = customer_model.create_customer("Listing Test", None, None, None, None)
        bid = booking_model.create_booking(cid, 1, "2026-08-01T14:00:00", "2026-08-03T12:00:00", 0, "")
        booking_model.set_booking_rooms(bid, [{"room_id": 1, "price_snapshot": 500000}])
        bookings = booking_model.get_bookings(hotel_id=1)
        assert len(bookings) >= 1
