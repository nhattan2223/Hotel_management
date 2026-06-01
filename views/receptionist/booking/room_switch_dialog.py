"""
RoomSwitchDialog — đổi phòng giữa chừng cho booking đang Checked-in.
Cho phép lễ tân chọn phòng cũ (trong booking), phòng mới và ngày đổi.
Tiền được tính chính xác theo từng giai đoạn trong compute_invoice.
"""
import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QComboBox, QDateTimeEdit,
    QFrame, QMessageBox,
)
from PyQt6.QtCore import QDateTime, QTime, Qt

from models import room_model, booking_model
from models.booking_model import check_room_availability
from services.booking_service import switch_room


class RoomSwitchDialog(QDialog):
    """Dialog đổi phòng giữa chừng cho một booking đang Checked-in."""

    def __init__(self, booking: dict, hotel_id: int, parent=None):
        super().__init__(parent)
        self.booking    = booking
        self.hotel_id   = hotel_id
        self._all_rooms = room_model.get_rooms(hotel_id)

        self.setWindowTitle(f"🔄 Đổi phòng — Booking #{booking['id']}")
        self.setMinimumWidth(520)
        self.setFixedHeight(460)
        self._setup_ui()
        self._populate_old_rooms()

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel(f"🔄 Đổi phòng — Booking #{self.booking['id']}")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        info = QFrame()
        info.setObjectName("Card")
        info_l = QFormLayout(info)
        info_l.setContentsMargins(16, 10, 16, 10)
        info_l.setSpacing(6)

        ci = datetime.datetime.fromisoformat(self.booking["check_in_date"]).strftime("%d/%m/%Y %H:%M")
        co = datetime.datetime.fromisoformat(self.booking["check_out_date"]).strftime("%d/%m/%Y %H:%M")
        info_l.addRow(QLabel("<b>Khách:</b>"),     QLabel(self.booking["customer_name"]))
        info_l.addRow(QLabel("<b>Check-in:</b>"),  QLabel(ci))
        info_l.addRow(QLabel("<b>Check-out:</b>"), QLabel(co))
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(12)

        self.old_room_combo = QComboBox()
        self.old_room_combo.setMinimumWidth(300)
        self.old_room_combo.currentIndexChanged.connect(self._refresh_new_rooms)
        form.addRow("Phòng cần đổi:", self.old_room_combo)

        self.switch_dt = QDateTimeEdit()
        self.switch_dt.setCalendarPopup(True)
        self.switch_dt.setDisplayFormat("dd/MM/yyyy HH:mm")
        now = datetime.datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        self.switch_dt.setDateTime(
            QDateTime(now.year, now.month, now.day, now.hour, now.minute)
        )
        self.switch_dt.dateTimeChanged.connect(self._refresh_new_rooms)
        form.addRow("Ngày đổi phòng:", self.switch_dt)

        self.new_room_combo = QComboBox()
        self.new_room_combo.setMinimumWidth(300)
        self.new_room_combo.currentIndexChanged.connect(self._update_preview)
        form.addRow("Phòng mới:", self.new_room_combo)

        layout.addLayout(form)

        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("Card")
        self.preview_frame.setStyleSheet(
            "QFrame#Card { background: #E0F7F5; border-radius: 10px; border: 1px solid #B2DFDB; }"
        )
        prev_l = QVBoxLayout(self.preview_frame)
        prev_l.setContentsMargins(16, 10, 16, 10)
        prev_l.setSpacing(4)
        self.preview_lbl = QLabel("Chọn phòng để xem dự tính tiền")
        self.preview_lbl.setStyleSheet("color: #1A2E35; font-size: 13px;")
        self.preview_lbl.setWordWrap(True)
        prev_l.addWidget(self.preview_lbl)
        layout.addWidget(self.preview_frame)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setObjectName("SecondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        self.confirm_btn = QPushButton("✅ Xác nhận đổi phòng")
        self.confirm_btn.setObjectName("PrimaryBtn")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self._confirm)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.confirm_btn)
        layout.addLayout(btn_row)

    # ── Data helpers ───────────────────────────────────────────────────────────

    def _populate_old_rooms(self):
        """Điền danh sách phòng hiện tại của booking vào combo phòng cũ.
        Lấy hoàn toàn từ BookingRooms — nguồn chính thức duy nhất.
        """
        self.old_room_combo.blockSignals(True)
        self.old_room_combo.clear()

        booked_rooms = booking_model.get_booking_rooms(self.booking["id"])
        for br in booked_rooms:
            room = next((r for r in self._all_rooms if r["id"] == br["room_id"]), None)
            if room:
                label = (f"Phòng {room['room_number']} – {room['type_name']} "
                         f"({int(room['price_per_night']):,}đ/đêm)")
                self.old_room_combo.addItem(label, room)

        self.old_room_combo.blockSignals(False)
        self._refresh_new_rooms()

    def _refresh_new_rooms(self):
        """Làm mới danh sách phòng mới — chỉ hiện phòng trống trong khoảng còn lại."""
        self.new_room_combo.blockSignals(True)
        self.new_room_combo.clear()

        old_room   = self.old_room_combo.currentData()
        switch_str = self.switch_dt.dateTime().toPyDateTime().isoformat()
        co_str     = self.booking["check_out_date"]

        # Lấy tất cả room_id đang trong booking này
        booked_ids = {br["room_id"]
                      for br in booking_model.get_booking_rooms(self.booking["id"])}

        for r in self._all_rooms:
            if old_room and r["id"] == old_room["id"]:
                continue
            if r["id"] in booked_ids:
                continue
            if not check_room_availability(r["id"], switch_str, co_str,
                                           exclude_booking_id=self.booking["id"]):
                continue
            label = (f"Phòng {r['room_number']} – {r['type_name']} "
                     f"({int(r['price_per_night']):,}đ/đêm)")
            self.new_room_combo.addItem(label, r)

        self.new_room_combo.blockSignals(False)
        self._update_preview()

    def _update_preview(self):
        """Hiển thị dự tính tiền sau khi đổi phòng."""
        old_room = self.old_room_combo.currentData()
        new_room = self.new_room_combo.currentData()

        if not old_room or not new_room:
            self.preview_lbl.setText("⚠️ Không có phòng phù hợp trong khoảng thời gian này.")
            self.confirm_btn.setEnabled(False)
            return

        switch_dt = self.switch_dt.dateTime().toPyDateTime()
        ci        = datetime.datetime.fromisoformat(self.booking["check_in_date"])
        co        = datetime.datetime.fromisoformat(self.booking["check_out_date"])

        if switch_dt <= ci:
            self.preview_lbl.setText("⚠️ Ngày đổi phòng phải sau ngày check-in.")
            self.confirm_btn.setEnabled(False)
            return
        if switch_dt >= co:
            self.preview_lbl.setText("⚠️ Ngày đổi phòng phải trước ngày check-out.")
            self.confirm_btn.setEnabled(False)
            return

        nights_old = max((switch_dt.date() - ci.date()).days, 0)
        nights_new = max((co.date() - switch_dt.date()).days, 0)

        amt_old = nights_old * float(old_room["price_per_night"])
        amt_new = nights_new * float(new_room["price_per_night"])
        total   = amt_old + amt_new

        switch_str = switch_dt.strftime("%d/%m/%Y")
        text = (
            f"📋 <b>Dự tính tiền phòng sau khi đổi:</b><br>"
            f"• Phòng <b>{old_room['room_number']}</b> ({old_room['type_name']}): "
            f"{nights_old} đêm × {int(old_room['price_per_night']):,}đ "
            f"= <b>{int(amt_old):,}đ</b><br>"
            f"• Phòng <b>{new_room['room_number']}</b> ({new_room['type_name']}): "
            f"{nights_new} đêm × {int(new_room['price_per_night']):,}đ "
            f"= <b>{int(amt_new):,}đ</b><br>"
            f"🏷️ <b>Tổng tiền phòng: {int(total):,}đ</b> "
            f"<small>(đổi từ ngày {switch_str})</small>"
        )
        self.preview_lbl.setText(text)
        self.confirm_btn.setEnabled(True)

    # ── Confirm ────────────────────────────────────────────────────────────────

    def _confirm(self):
        old_room  = self.old_room_combo.currentData()
        new_room  = self.new_room_combo.currentData()
        switch_dt = self.switch_dt.dateTime().toPyDateTime()

        if not old_room or not new_room:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn đủ phòng.")
            return

        msg = (
            f"Xác nhận đổi phòng?\n\n"
            f"Phòng cũ: {old_room['room_number']} ({old_room['type_name']})\n"
            f"Phòng mới: {new_room['room_number']} ({new_room['type_name']})\n"
            f"Từ ngày: {switch_dt.strftime('%d/%m/%Y %H:%M')}"
        )
        r = QMessageBox.question(self, "Xác nhận đổi phòng", msg)
        if r != QMessageBox.StandardButton.Yes:
            return

        result = switch_room(
            self.booking["id"],
            old_room["id"],
            new_room["id"],
            switch_dt.isoformat(),
        )

        if result["ok"]:
            QMessageBox.information(
                self, "Thành công",
                f"Đã đổi từ phòng {old_room['room_number']} sang "
                f"phòng {new_room['room_number']} thành công!\n"
                f"Tiền sẽ được tính theo 2 giai đoạn trên hóa đơn."
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", result["error"])
