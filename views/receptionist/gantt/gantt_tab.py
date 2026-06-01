from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QMessageBox)
from PyQt6.QtCore import Qt
from models import booking_model, room_model
from views.widgets.gantt_chart import GanttChartWidget


class GanttTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self.hotel_id = user["hotel_id"]
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("📅 Lịch đặt phòng")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        sub = QLabel("Click vào booking để xem chi tiết")
        sub.setObjectName("PageSubtitle")
        hdr.addStretch()
        hdr.addWidget(sub)
        layout.addLayout(hdr)

        self.gantt = GanttChartWidget()
        self.gantt.booking_clicked.connect(self._on_booking_click)
        layout.addWidget(self.gantt)

    def refresh(self):
        rooms    = room_model.get_rooms(self.hotel_id)
        bookings = booking_model.get_all_bookings_for_gantt(self.hotel_id)
        self.gantt.set_data(rooms, bookings)

    def _on_booking_click(self, booking_id: int, room_id: int):
        """Hiển thị popup chi tiết booking khi click vào segment trên Gantt.
        room_id là id phòng của segment được click (từ get_all_bookings_for_gantt).
        Tra cứu thông tin phòng cụ thể từ BookingRooms / RoomChargeHistory.
        """
        import datetime
        bk = booking_model.get_booking(booking_id)
        if not bk:
            return

        # Tìm thông tin phòng theo room_id được click
        room_number = None
        type_name   = None

        # Ưu tiên: RoomChargeHistory (chứa lịch sử đổi phòng)
        charges = booking_model.get_room_charges(booking_id)
        charge = next((c for c in charges if c.get("room_id") == room_id), None)
        if charge:
            room_number = charge.get("room_number")
            type_name   = charge.get("room_type_name")

        # Fallback: BookingRooms
        if not room_number:
            brs = booking_model.get_booking_rooms(booking_id)
            br = next((b for b in brs if b.get("room_id") == room_id), None)
            if br:
                room_number = br.get("room_number")
                type_name   = br.get("type_name")

        # Fallback cuối: dùng room_number_all từ get_booking
        if not room_number:
            room_number = bk.get("room_number", "N/A")
            type_name   = bk.get("type_name", "")

        ci = datetime.datetime.fromisoformat(bk["check_in_date"]).strftime("%d/%m/%Y")
        co = datetime.datetime.fromisoformat(bk["check_out_date"]).strftime("%d/%m/%Y")
        msg = (f"Booking #{booking_id}\n"
               f"Khách: {bk['customer_name']}\n"
               f"Phòng: {room_number} ({type_name})\n"
               f"Check-in: {ci}  →  Check-out: {co}\n"
               f"Trạng thái: {bk['status']}\n"
               f"Cọc: {int(bk.get('deposit_amount', 0)):,} đ")
        QMessageBox.information(self, f"Chi tiết Booking #{booking_id}", msg)
