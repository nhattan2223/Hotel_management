import datetime

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QVBoxLayout, QFrame, QGroupBox,
)

from models import room_model, booking_model
from services.booking_service import (
    compute_room_display_status, do_checkin, do_checkout,
    format_booking_datetime, is_checkin_time_reached,
)
from utils.config import (
    BOOKING_STATUS_VN, BOOKING_STATUS_COLOR,
    STATUS_DIRTY, STATUS_CLEAN,
    BOOKING_RESERVED, BOOKING_CHECKED_IN,
)


class RoomActionDialog(QDialog):
    """Dialog shown when clicking a room card – shows details + actions."""
    def __init__(self, room: dict, user: dict, parent=None):
        super().__init__(parent)
        self.room = room
        self.user = user
        self.display_status = compute_room_display_status(room)
        self.setWindowTitle(f"Phòng {room['room_number']} – Chi tiết")
        self.setFixedWidth(480)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel(f"🛏 Phòng {self.room['room_number']}")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        STATUS_VN = BOOKING_STATUS_VN
        STATUS_COLORS = BOOKING_STATUS_COLOR
        STATUS_COLOR = BOOKING_STATUS_COLOR

        info_w = QFrame()
        info_w.setObjectName("Card")
        info_l = QFormLayout(info_w)
        info_l.setContentsMargins(16, 12, 16, 12)

        def row(k, v, color=None):
            lbl = QLabel(v)
            if color:
                lbl.setStyleSheet(f"color: {color}; font-weight: bold;")
            info_l.addRow(QLabel(f"<b>{k}</b>"), lbl)

        row("Loại phòng:", self.room["type_name"])
        row("Tầng:", str(self.room["floor"] or "—"))
        row("Giá/đêm:", f"{int(self.room['price_per_night']):,} đ")
        row("Trạng thái:", STATUS_VN.get(self.display_status, self.display_status),
            STATUS_COLOR.get(self.display_status))
        row("Vệ sinh:", "Sạch ✅" if self.room["housekeeping"] == STATUS_CLEAN else "Đang dọn 🧹")
        layout.addWidget(info_w)

        bookings = booking_model.get_bookings_for_room(self.room["id"])
        active_booking = next((b for b in bookings if b["status"] in (BOOKING_RESERVED, BOOKING_CHECKED_IN)), None)

        if active_booking:
            bk_frame = QFrame()
            bk_frame.setObjectName("Card")
            bk_l = QFormLayout(bk_frame)
            bk_l.setContentsMargins(16, 12, 16, 12)
            ci = datetime.datetime.fromisoformat(active_booking["check_in_date"]).strftime("%d/%m/%Y")
            co = datetime.datetime.fromisoformat(active_booking["check_out_date"]).strftime("%d/%m/%Y")
            bk_l.addRow(QLabel("<b>Booking #:</b>"), QLabel(str(active_booking["id"])))
            bk_l.addRow(QLabel("<b>Khách:</b>"), QLabel(active_booking["customer_name"]))
            bk_l.addRow(QLabel("<b>Check-in:</b>"), QLabel(ci))
            bk_l.addRow(QLabel("<b>Check-out:</b>"), QLabel(co))
            bk_l.addRow(QLabel("<b>Trạng thái:</b>"), QLabel(active_booking["status"]))
            layout.addWidget(bk_frame)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if active_booking and active_booking["status"] == BOOKING_RESERVED:
            if self.display_status != STATUS_DIRTY:
                ci_btn = QPushButton("✅ Check-in")
                ci_btn.setObjectName("PrimaryBtn")
                if not is_checkin_time_reached(active_booking):
                    ci_btn.setEnabled(False)
                    ci_btn.setToolTip(
                        f"Chỉ được check-in từ {format_booking_datetime(active_booking['check_in_date'])}"
                    )
                ci_btn.clicked.connect(lambda: self._do_checkin(active_booking["id"]))
                btn_row.addWidget(ci_btn)

        if active_booking and active_booking["status"] == BOOKING_CHECKED_IN:
            co_btn = QPushButton("🚪 Check-out")
            co_btn.setObjectName("WarningBtn")
            co_btn.clicked.connect(lambda: self._do_checkout(active_booking["id"]))
            btn_row.addWidget(co_btn)

        close_btn = QPushButton("Đóng")
        close_btn.setObjectName("SecondaryBtn")
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _do_checkin(self, bid):
        result = do_checkin(bid)
        if result["ok"]:
            QMessageBox.information(self, "Thành công", "Check-in thành công!")
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", result["error"])

    def _do_checkout(self, bid):
        result = do_checkout(bid, self.user["id"])
        if result["ok"]:
            QMessageBox.information(self, "Thành công", "Check-out thành công! Phòng chuyển sang trạng thái dọn dẹp.")
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", result["error"])
