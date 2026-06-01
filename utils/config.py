import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'hotel.db')

APP_NAME = "Hotel Management System"
APP_VERSION = "1.0.0"

# ── VAT ───────────────────────────────────────────────────
VAT_RATE = 0.08  # 8%

# ── Colors ────────────────────────────────────────────────
PRIMARY        = "#00B4A6"
PRIMARY_DARK   = "#008F83"
PRIMARY_DARKER = "#006B62"
PRIMARY_LIGHT  = "#E0F7F5"
PRIMARY_HOVER  = "#00CEC0"

ACCENT         = "#F5A623"
ACCENT_LIGHT   = "#FFF3DC"

BG_APP         = "#F0FAFA"
BG_CARD        = "#FFFFFF"
BG_SIDEBAR     = "#00B4A6"

TEXT_DARK      = "#1A2E35"
TEXT_MEDIUM    = "#4A6572"
TEXT_LIGHT     = "#8FA5AC"
TEXT_WHITE     = "#FFFFFF"

BORDER_COLOR   = "#D4ECEB"
SHADOW_COLOR   = "rgba(0,180,166,0.12)"

# ── Room status colors ────────────────────────────────────
COLOR_AVAILABLE  = "#27AE60"
COLOR_OCCUPIED   = "#E74C3C"
COLOR_RESERVED   = "#F39C12"
COLOR_DIRTY      = "#95A5A6"
COLOR_CLEANING   = "#95A5A6"

# ── Status labels (English) ───────────────────────────────
STATUS_AVAILABLE  = "Available"
STATUS_OCCUPIED   = "Occupied"
STATUS_RESERVED   = "Reserved"
STATUS_DIRTY      = "Dirty"
STATUS_CLEAN      = "Clean"

# ── Booking status ────────────────────────────────────────
BOOKING_RESERVED   = "Reserved"
BOOKING_CHECKED_IN = "Checked-in"
BOOKING_CHECKED_OUT = "Checked-out"
BOOKING_CANCELLED  = "Cancelled"

# ── Roles ─────────────────────────────────────────────────
ROLE_ADMIN       = "admin"
ROLE_RECEPTIONIST = "receptionist"
ROLE_HOUSEKEEPING = "housekeeping"
ROLE_CHEF        = "chef"

# ── Payment ───────────────────────────────────────────────
PAYMENT_CASH     = "Cash"
PAYMENT_CARD     = "Card"
PAYMENT_TRANSFER = "Transfer"

# Payment status (Invoices)
PAYMENT_STATUS_UNPAID = "Unpaid"
PAYMENT_STATUS_PAID = "Paid"

# Payment options shown in invoice UI (keep labels centralized)
PAYMENT_METHODS = [
    "Tiền mặt (Cash)",
    "Thẻ ngân hàng (Card)",
    "Chuyển khoản (Transfer)",
]
PAYMENT_CODES = [PAYMENT_CASH, PAYMENT_CARD, PAYMENT_TRANSFER]

# Export invoice is allowed after this booking status
INVOICE_EXPORT_STATUS = BOOKING_CHECKED_OUT

# ── Booking status Vietnamese labels (dùng chung toàn app) ─
BOOKING_STATUS_VN = {
    "Reserved":    "Đã đặt",
    "Checked-in":  "Đang ở",
    "Checked-out": "Đã trả",
    "Cancelled":   "Đã hủy",
}

# ── Booking status colors (dùng chung toàn app) ───────────
BOOKING_STATUS_COLOR = {
    "Reserved":    "#F39C12",
    "Checked-in":  "#27AE60",
    "Checked-out": "#95A5A6",
    "Cancelled":   "#E74C3C",
}

# ── Room display status Vietnamese labels ─────────────────
ROOM_STATUS_VN = {
    "Available": "Trống",
    "Occupied":  "Đang ở",
    "Reserved":  "Đã đặt",
    "Dirty":     "Đang dọn",
}
