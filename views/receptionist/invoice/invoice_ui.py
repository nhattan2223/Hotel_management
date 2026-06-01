import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from utils.config import (
    BOOKING_STATUS_VN,
    INVOICE_EXPORT_STATUS,
    PAYMENT_CODES,
    PAYMENT_METHODS,
)
from views.receptionist.invoice.invoice_helpers import (
    _bold,
    _make_table,
    _section_lbl,
)


def setup_invoice_ui(tab: QWidget) -> None:
    """
    Build all widgets/layouts for InvoiceTab.

    This function only constructs UI and wires signals.
    Data loading is handled by tab.refresh/tab._load_invoice.
    """
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(16)

    # ── Header ────────────────────────────────────────────
    hdr = QHBoxLayout()
    title = QLabel("🧾 Hóa đơn")
    title.setObjectName("PageTitle")
    hdr.addWidget(title)
    hdr.addStretch()
    refresh_btn = QPushButton("🔄 Làm mới")
    refresh_btn.setObjectName("SecondaryBtn")
    refresh_btn.clicked.connect(tab.refresh)
    hdr.addWidget(refresh_btn)
    layout.addLayout(hdr)

    # ── Booking selector ──────────────────────────────────
    sel_row = QHBoxLayout()
    sel_row.addWidget(QLabel("Trạng thái:"))
    tab.status_combo = QComboBox()
    tab.status_combo.setMinimumWidth(120)
    tab.status_combo.addItem("Tất cả", None)
    for eng, vn in BOOKING_STATUS_VN.items():
        tab.status_combo.addItem(vn, eng)
    sel_row.addWidget(tab.status_combo)
    sel_row.addSpacing(12)
    sel_row.addWidget(QLabel("Chọn booking:"))
    tab.booking_combo = QComboBox()
    tab.booking_combo.setMinimumWidth(400)
    sel_row.addWidget(tab.booking_combo)
    sel_row.addStretch()
    layout.addLayout(sel_row)

    # Empty state
    tab.empty_lbl = QLabel("⚠️  Chưa có booking nào. Vui lòng tạo booking trước.")
    tab.empty_lbl.setStyleSheet(
        "background:#FEF3DC; color:#8B6914; border-radius:8px; padding:10px 14px; font-size:13px;"
    )
    tab.empty_lbl.setVisible(False)
    layout.addWidget(tab.empty_lbl)

    # ── Scrollable invoice preview ────────────────────────
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    preview_container = QWidget()
    preview_layout = QVBoxLayout(preview_container)
    preview_layout.setContentsMargins(0, 0, 8, 0)
    preview_layout.setSpacing(14)

    # Guest info card
    tab.guest_frame = QFrame()
    tab.guest_frame.setObjectName("Card")
    guest_l = QFormLayout(tab.guest_frame)
    guest_l.setContentsMargins(20, 14, 20, 14)
    guest_l.setSpacing(8)

    tab.lbl_customer = QLabel("—")
    tab.lbl_idcard = QLabel("—")
    tab.lbl_phone = QLabel("—")
    tab.lbl_room = QLabel("—")
    tab.lbl_type = QLabel("—")
    tab.lbl_checkin = QLabel("—")
    tab.lbl_checkout = QLabel("—")
    tab.lbl_nights = QLabel("—")
    tab.lbl_status = QLabel("—")
    tab.lbl_cashier = QLabel("—")

    for lbl in [
        tab.lbl_customer,
        tab.lbl_idcard,
        tab.lbl_phone,
        tab.lbl_room,
        tab.lbl_type,
        tab.lbl_checkin,
        tab.lbl_checkout,
        tab.lbl_nights,
        tab.lbl_status,
        tab.lbl_cashier,
    ]:
        lbl.setStyleSheet("font-size:13px; color:#1A2E35;")

    guest_l.addRow(_bold("Khách hàng:"), tab.lbl_customer)
    guest_l.addRow(_bold("CCCD/Hộ chiếu:"), tab.lbl_idcard)
    guest_l.addRow(_bold("Điện thoại:"), tab.lbl_phone)
    guest_l.addRow(_bold("Phòng:"), tab.lbl_room)
    guest_l.addRow(_bold("Loại phòng:"), tab.lbl_type)
    guest_l.addRow(_bold("Check-in:"), tab.lbl_checkin)
    guest_l.addRow(_bold("Check-out:"), tab.lbl_checkout)
    guest_l.addRow(_bold("Số đêm:"), tab.lbl_nights)
    guest_l.addRow(_bold("Trạng thái:"), tab.lbl_status)
    guest_l.addRow(_bold("Người thu tiền:"), tab.lbl_cashier)
    preview_layout.addWidget(tab.guest_frame)

    # Room charge table
    preview_layout.addWidget(_section_lbl("🛏 Tiền phòng"))
    tab.room_table = _make_table(["Phòng", "Loại", "Số đêm", "Giá/đêm (đ)", "Thành tiền (đ)"])
    preview_layout.addWidget(tab.room_table)

    # Services table
    preview_layout.addWidget(_section_lbl("🛎 Dịch vụ"))
    tab.svc_table = _make_table(["Dịch vụ", "Số lượng", "Đơn giá (đ)", "Thành tiền (đ)"])
    preview_layout.addWidget(tab.svc_table)

    # Meals table
    preview_layout.addWidget(_section_lbl("🍽 Ẩm thực (F&B)"))
    tab.meal_table = _make_table(["Món ăn", "Bữa", "Số lượng", "Đơn giá (đ)", "Thành tiền (đ)"])
    preview_layout.addWidget(tab.meal_table)

    # Summary card
    summ_frame = QFrame()
    summ_frame.setObjectName("Card")
    summ_frame.setStyleSheet(
        "QFrame#Card { background:#E0F7F5; border-radius:14px; border:1px solid #B2DFDB; }"
    )
    summ_l = QFormLayout(summ_frame)
    summ_l.setContentsMargins(24, 16, 24, 16)
    summ_l.setSpacing(10)

    tab.s_room = QLabel("0 đ")
    tab.s_svc = QLabel("0 đ")
    tab.s_meal = QLabel("0 đ")
    tab.s_tax = QLabel("0 đ")
    tab.s_disc = QLabel("0 đ")
    tab.s_total = QLabel("0 đ")
    tab.s_total.setStyleSheet("font-size:20px; font-weight:bold; color:#00B4A6;")
    for w in [tab.s_room, tab.s_svc, tab.s_meal, tab.s_tax, tab.s_disc]:
        w.setStyleSheet("font-size:14px; color:#1A2E35;")

    summ_l.addRow(_bold("Tiền phòng:"), tab.s_room)
    summ_l.addRow(_bold("Dịch vụ:"), tab.s_svc)
    summ_l.addRow(_bold("Ẩm thực:"), tab.s_meal)
    summ_l.addRow(_bold("VAT (8%):"), tab.s_tax)
    summ_l.addRow(_bold("Đặt cọc / Giảm giá:"), tab.s_disc)

    # Divider
    div = QFrame()
    div.setFixedHeight(1)
    div.setStyleSheet("background:#B2DFDB; margin:4px 0;")
    summ_l.addRow(div)

    summ_l.addRow(_bold("💰 TỔNG THANH TOÁN:", size=14), tab.s_total)
    preview_layout.addWidget(summ_frame)

    preview_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    scroll.setWidget(preview_container)
    layout.addWidget(scroll, 1)

    # ── Action bar ────────────────────────────────────────
    action_frame = QFrame()
    action_frame.setObjectName("Card")
    action_l = QHBoxLayout(action_frame)
    action_l.setContentsMargins(16, 12, 16, 12)
    action_l.setSpacing(12)

    action_l.addWidget(_bold("Phương thức thanh toán:"))
    tab.payment_combo = QComboBox()
    tab.payment_combo.setMinimumWidth(200)
    for m in PAYMENT_METHODS:
        tab.payment_combo.addItem(m)
    action_l.addWidget(tab.payment_combo)

    action_l.addStretch()

    tab.pdf_btn = QPushButton("📄 Xuất hóa đơn PDF")
    tab.pdf_btn.setObjectName("PrimaryBtn")
    tab.pdf_btn.setFixedHeight(42)
    tab.pdf_btn.setMinimumWidth(180)
    tab.pdf_btn.clicked.connect(tab._export_pdf)
    action_l.addWidget(tab.pdf_btn)

    layout.addWidget(action_frame)

    # Connect signal AFTER all widgets built
    tab.status_combo.currentIndexChanged.connect(tab.refresh)
    tab.booking_combo.currentIndexChanged.connect(tab._load_invoice)

