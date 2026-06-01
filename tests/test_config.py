"""Test configuration constants."""
from utils import config


class TestConfig:
    def test_app_info(self):
        assert config.APP_NAME
        assert config.APP_VERSION

    def test_vat_rate(self):
        assert config.VAT_RATE == 0.08

    def test_status_constants(self):
        assert config.STATUS_AVAILABLE == "Available"
        assert config.STATUS_OCCUPIED == "Occupied"
        assert config.STATUS_DIRTY == "Dirty"
        assert config.STATUS_CLEAN == "Clean"

    def test_booking_status(self):
        assert config.BOOKING_RESERVED == "Reserved"
        assert config.BOOKING_CHECKED_IN == "Checked-in"
        assert config.BOOKING_CHECKED_OUT == "Checked-out"
        assert config.BOOKING_CANCELLED == "Cancelled"

    def test_payment(self):
        assert len(config.PAYMENT_METHODS) == 3
        assert len(config.PAYMENT_CODES) == 3

    def test_vietnamese_labels(self):
        vn = config.BOOKING_STATUS_VN
        assert vn["Reserved"] == "Đã đặt"
        assert vn["Checked-in"] == "Đang ở"
        assert vn["Checked-out"] == "Đã trả"
        assert vn["Cancelled"] == "Đã hủy"

    def test_invoice_export_status(self):
        assert config.INVOICE_EXPORT_STATUS == config.BOOKING_CHECKED_OUT

    def test_db_path(self):
        assert config.DB_PATH.endswith("hotel.db")
