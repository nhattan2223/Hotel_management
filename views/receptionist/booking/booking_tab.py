"""
BookingTab — bảng quản lý booking cho receptionist.
Dialog tạo/sửa booking nằm ở booking_dialog.py
"""
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QComboBox,
    QMessageBox, QHeaderView,
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QTimer

from utils.config import (BOOKING_STATUS_VN, BOOKING_STATUS_COLOR,
                          BOOKING_RESERVED, BOOKING_CHECKED_IN)
from models import booking_model
from services.booking_service import (
    cancel_expired_unchecked_bookings,
    checkout_expired_checkedin_bookings,
    do_checkin, do_checkout,
    format_booking_datetime,
    is_checkin_time_reached,
)
from views.receptionist.booking.booking_dialog import BookingDialog
from views.receptionist.booking.room_switch_dialog import RoomSwitchDialog

STATUS_VN     = BOOKING_STATUS_VN
STATUS_COLORS = BOOKING_STATUS_COLOR


class BookingTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user     = user
        self.hotel_id = user["hotel_id"]
        self._setup_ui()
        self.refresh()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(30_000)

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("📋 Quản lý Booking")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Tất cả", None)
        for k, v in STATUS_VN.items():
            self.filter_combo.addItem(v, k)
        self.filter_combo.currentIndexChanged.connect(self.refresh)
        hdr.addWidget(QLabel("Trạng thái:"))
        hdr.addWidget(self.filter_combo)

        add_btn = QPushButton("+ Tạo booking")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.clicked.connect(self._add_booking)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Khách hàng", "Phòng", "Check-in", "Check-out",
            "Đêm", "Cọc (đ)", "Trạng thái", "Nhân viên", "Thao tác",
        ])
        hv = self.table.horizontalHeader()
        hv.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hv.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hv.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(9, 200)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    # ── Data ───────────────────────────────────────────────────────────────────

    def refresh(self):
        cancelled   = cancel_expired_unchecked_bookings(self.hotel_id)
        checked_out = checkout_expired_checkedin_bookings(self.hotel_id)
        if cancelled or checked_out:
            self._notify_gantt()

        status_filter = self.filter_combo.currentData()
        bookings = booking_model.get_bookings(self.hotel_id, status_filter)
        self.table.setRowCount(len(bookings))

        for i, b in enumerate(bookings):
            ci     = datetime.datetime.fromisoformat(b["check_in_date"])
            co     = datetime.datetime.fromisoformat(b["check_out_date"])
            nights = max((co - ci).days, 1)

            vals = [
                str(b["id"]),
                b["customer_name"],
                ", ".join(br["room_number"] for br in booking_model.get_booking_rooms(b["id"])) or f"{b['room_number']} ({b['type_name']})",
                ci.strftime("%d/%m/%Y"),
                co.strftime("%d/%m/%Y"),
                str(nights),
                f"{int(b['deposit_amount']):,}",
                STATUS_VN.get(b["status"], b["status"]),
                b["staff_name"],
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 7:
                    item.setForeground(
                        QColor(STATUS_COLORS.get(b["status"], "#1A2E35"))
                    )
                self.table.setItem(i, j, item)

            self.table.setCellWidget(i, 9, self._make_action_buttons(b))
            self.table.setRowHeight(i, 44)

    def _make_action_buttons(self, b: dict) -> QWidget:
        btn_w = QWidget()
        btn_l = QHBoxLayout(btn_w)
        btn_l.setContentsMargins(4, 2, 4, 2)
        btn_l.setSpacing(4)

        if b["status"] == BOOKING_RESERVED:
            ci_btn = QPushButton("✅ C-in")
            ci_btn.setObjectName("PrimaryBtn")
            ci_btn.setFixedHeight(28)
            if not is_checkin_time_reached(b):
                ci_btn.setEnabled(False)
                ci_btn.setToolTip(
                    f"Chỉ được check-in từ {format_booking_datetime(b['check_in_date'])}"
                )
            ci_btn.clicked.connect(lambda _, bid=b["id"]: self._do_checkin(bid))
            btn_l.addWidget(ci_btn)

            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("IconBtn")
            edit_btn.setToolTip("Sửa booking")
            edit_btn.clicked.connect(lambda _, bid=b["id"]: self._edit_booking(bid))
            btn_l.addWidget(edit_btn)

            cancel_btn = QPushButton("❌")
            cancel_btn.setObjectName("IconBtn")
            cancel_btn.setToolTip("Hủy booking")
            cancel_btn.clicked.connect(lambda _, bid=b["id"]: self._cancel_booking(bid))
            btn_l.addWidget(cancel_btn)

        elif b["status"] == BOOKING_CHECKED_IN:
            co_btn = QPushButton("🚪 C-out")
            co_btn.setObjectName("WarningBtn")
            co_btn.setFixedHeight(28)
            co_btn.clicked.connect(lambda _, bid=b["id"]: self._do_checkout(bid))
            btn_l.addWidget(co_btn)

            switch_btn = QPushButton("🔄")
            switch_btn.setObjectName("IconBtn")
            switch_btn.setToolTip("Đổi phòng giữa chừng")
            switch_btn.setFixedHeight(28)
            switch_btn.clicked.connect(lambda _, bid=b["id"]: self._switch_room(bid))
            btn_l.addWidget(switch_btn)

            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("IconBtn")
            edit_btn.setToolTip("Sửa booking")
            edit_btn.clicked.connect(lambda _, bid=b["id"]: self._edit_booking(bid))
            btn_l.addWidget(edit_btn)

        return btn_w

    # ── Actions ────────────────────────────────────────────────────────────────

    def _add_booking(self):
        dlg = BookingDialog(self.user, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self._notify_gantt()

    def _edit_booking(self, bid):
        bk = booking_model.get_booking(bid)
        if not bk:
            return
        dlg = BookingDialog(self.user, booking=bk, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self._notify_gantt()

    def _cancel_booking(self, bid):
        r = QMessageBox.question(self, "Xác nhận", "Hủy booking này?")
        if r == QMessageBox.StandardButton.Yes:
            booking_model.cancel_booking(bid)
            self.refresh()
            self._notify_gantt()

    def _do_checkin(self, bid):
        result = do_checkin(bid)
        if result["ok"]:
            QMessageBox.information(self, "Thành công", "Check-in thành công!")
            self.refresh()
        else:
            QMessageBox.warning(self, "Lỗi", result["error"])

    def _do_checkout(self, bid):
        result = do_checkout(bid, self.user["id"])
        if result["ok"]:
            QMessageBox.information(
                self, "Thành công",
                "Check-out thành công!\nPhòng chuyển sang trạng thái đang dọn.",
            )
            self.refresh()
        else:
            QMessageBox.warning(self, "Lỗi", result["error"])

    def _switch_room(self, bid):
        bk = booking_model.get_booking(bid)
        if not bk:
            return
        dlg = RoomSwitchDialog(bk, self.hotel_id, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self._notify_gantt()

    def _notify_gantt(self):
        try:
            stack = self.parent()
            if stack:
                win = stack.parent()
                if win and hasattr(win, "_tabs"):
                    gantt = win._tabs.get("gantt")
                    if gantt and hasattr(gantt, "refresh"):
                        gantt.refresh()
        except Exception:
            pass