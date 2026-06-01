from PyQt6.QtWidgets import (
    QVBoxLayout, QFormLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QDateTimeEdit,
    QDoubleSpinBox, QTextEdit, QListWidget,
    QListWidgetItem, QAbstractItemView, QFrame,
    QScrollArea, QWidget,
)
from PyQt6.QtCore import QDateTime, QTime, Qt

from utils.config import BOOKING_STATUS_VN


STATUS_VN = BOOKING_STATUS_VN


def setup_booking_dialog_ui(dialog) -> None:
    outer = QVBoxLayout(dialog)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    outer.addWidget(scroll)

    container = QWidget()
    scroll.setWidget(container)

    layout = QVBoxLayout(container)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(14)

    # ── Customer section ───────────────────────────────────────────────────
    cust_lbl = QLabel("THÔNG TIN KHÁCH HÀNG")
    cust_lbl.setObjectName("SectionHeader")
    layout.addWidget(cust_lbl)

    form = QFormLayout()
    form.setSpacing(12)

    id_row = QHBoxLayout()
    dialog.id_card_input = QLineEdit()
    dialog.id_card_input.setPlaceholderText("Nhập CCCD để tìm / tạo khách")
    search_btn = QPushButton("🔍 Tìm")
    search_btn.setObjectName("SecondaryBtn")
    search_btn.clicked.connect(dialog._search_customer)
    id_row.addWidget(dialog.id_card_input)
    id_row.addWidget(search_btn)
    form.addRow("CCCD/Hộ chiếu:", id_row)

    dialog.cust_name    = QLineEdit(); dialog.cust_name.setPlaceholderText("Họ và tên")
    dialog.cust_phone   = QLineEdit(); dialog.cust_phone.setPlaceholderText("Số điện thoại")
    dialog.cust_email   = QLineEdit()
    dialog.cust_address = QLineEdit()
    form.addRow("Họ tên *:",   dialog.cust_name)
    form.addRow("Điện thoại:", dialog.cust_phone)
    form.addRow("Email:",      dialog.cust_email)
    form.addRow("Địa chỉ:",    dialog.cust_address)
    layout.addLayout(form)

    # ── Booking section ────────────────────────────────────────────────────
    bk_lbl = QLabel("THÔNG TIN ĐẶT PHÒNG")
    bk_lbl.setObjectName("SectionHeader")
    layout.addWidget(bk_lbl)

    form2 = QFormLayout()
    form2.setSpacing(12)

    dialog.checkin_dt = QDateTimeEdit()
    dialog.checkin_dt.setCalendarPopup(True)
    ci_now = QDateTime.currentDateTime(); ci_now.setTime(QTime(14, 0))
    dialog.checkin_dt.setDateTime(ci_now)
    dialog.checkin_dt.setDisplayFormat("dd/MM/yyyy HH:mm")
    dialog.checkin_dt.dateTimeChanged.connect(dialog._update_price_summary)

    dialog.checkout_dt = QDateTimeEdit()
    dialog.checkout_dt.setCalendarPopup(True)
    co_now = QDateTime.currentDateTime().addDays(1); co_now.setTime(QTime(12, 0))
    dialog.checkout_dt.setDateTime(co_now)
    dialog.checkout_dt.setDisplayFormat("dd/MM/yyyy HH:mm")
    dialog.checkout_dt.dateTimeChanged.connect(dialog._update_price_summary)

    form2.addRow("Ngày nhận phòng:", dialog.checkin_dt)
    form2.addRow("Ngày trả phòng:",  dialog.checkout_dt)

    dialog.deposit = QDoubleSpinBox()
    dialog.deposit.setRange(0, 100_000_000)
    dialog.deposit.setSingleStep(100_000)
    dialog.deposit.setSuffix(" đ")
    form2.addRow("Đặt cọc:", dialog.deposit)

    if dialog.booking:
        dialog.status_combo = QComboBox()
        for k, v in STATUS_VN.items():
            dialog.status_combo.addItem(v, k)
        form2.addRow("Trạng thái:", dialog.status_combo)

    dialog.note = QTextEdit()
    dialog.note.setMaximumHeight(60)
    dialog.note.setPlaceholderText("Ghi chú...")
    form2.addRow("Ghi chú:", dialog.note)
    layout.addLayout(form2)

    # ── Room picker ────────────────────────────────────────────────────────
    room_lbl = QLabel("CHỌN PHÒNG")
    room_lbl.setObjectName("SectionHeader")
    layout.addWidget(room_lbl)

    filter_row = QHBoxLayout()
    dialog.room_type_combo = QComboBox()
    dialog.room_type_combo.setFixedWidth(160)
    dialog._load_room_types()
    dialog.room_type_combo.currentIndexChanged.connect(dialog._refresh_available_list)
    filter_row.addWidget(QLabel("Lọc loại:"))
    filter_row.addWidget(dialog.room_type_combo)
    filter_row.addStretch()
    layout.addLayout(filter_row)

    panels = QHBoxLayout()
    panels.setSpacing(12)

    left = QVBoxLayout()
    left.addWidget(QLabel("Phòng trống:"))
    dialog.available_list = QListWidget()
    dialog.available_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    dialog.available_list.setFixedHeight(160)
    dialog.available_list.itemDoubleClicked.connect(dialog._add_selected)
    left.addWidget(dialog.available_list)
    add_btn = QPushButton("➕ Thêm vào booking")
    add_btn.setObjectName("SecondaryBtn")
    add_btn.clicked.connect(dialog._add_selected)
    left.addWidget(add_btn)
    panels.addLayout(left)

    right = QVBoxLayout()
    right.addWidget(QLabel("Phòng đã chọn:"))
    dialog.chosen_list = QListWidget()
    dialog.chosen_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    dialog.chosen_list.setFixedHeight(160)
    right.addWidget(dialog.chosen_list)
    remove_btn = QPushButton("➖ Bỏ phòng")
    remove_btn.setObjectName("SecondaryBtn")
    remove_btn.clicked.connect(dialog._remove_selected)
    right.addWidget(remove_btn)
    panels.addLayout(right)

    layout.addLayout(panels)

    dialog.price_summary = QLabel("")
    dialog.price_summary.setObjectName("PriceSummary")
    dialog.price_summary.setAlignment(Qt.AlignmentFlag.AlignRight)
    layout.addWidget(dialog.price_summary)

    # ── Buttons ────────────────────────────────────────────────────────────
    btn_row = QHBoxLayout()
    btn_row.addStretch()
    cancel_btn = QPushButton("Hủy")
    cancel_btn.setObjectName("SecondaryBtn")
    cancel_btn.clicked.connect(dialog.reject)
    save_btn = QPushButton("💾 Lưu booking")
    save_btn.setObjectName("PrimaryBtn")
    save_btn.clicked.connect(dialog._save)
    btn_row.addWidget(cancel_btn)
    btn_row.addWidget(save_btn)
    layout.addLayout(btn_row)

    dialog._load_all_rooms()
