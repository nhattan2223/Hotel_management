from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QScrollArea, QFrame, QGridLayout,
                              QDialog)
from PyQt6.QtCore import Qt, QTimer
from utils.config import (
    STATUS_AVAILABLE, STATUS_OCCUPIED, STATUS_DIRTY, BOOKING_RESERVED,
)
from models import room_model
from services.booking_service import compute_room_display_status
from views.widgets.room_card import RoomCard
from views.receptionist.rooms.room_action_dialog import RoomActionDialog


class ReceptionRoomsTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self.hotel_id = user["hotel_id"]
        self._setup_ui()
        self.refresh()

        # Auto-refresh every 30s
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(30_000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("🛏 Danh sách Phòng")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.setObjectName("SecondaryBtn")
        refresh_btn.clicked.connect(self.refresh)
        hdr.addWidget(refresh_btn)
        layout.addLayout(hdr)

        # Legend
        legend = QHBoxLayout()
        legend.addWidget(QLabel("Chú thích:"))
        for color, label in [("#27AE60", "Trống"), ("#E74C3C", "Đang ở"),
                              ("#F39C12", "Đã đặt"), ("#95A5A6", "Đang dọn")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 18px;")
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #4A6572; font-size: 12px; margin-right: 12px;")
            legend.addWidget(dot)
            legend.addWidget(lbl)
        legend.addStretch()
        layout.addLayout(legend)

        # Scroll area for room grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

        # Summary bar
        self.summary_lbl = QLabel()
        self.summary_lbl.setStyleSheet("color: #4A6572; font-size: 12px;")
        layout.addWidget(self.summary_lbl)

    def refresh(self):
        # Clear grid
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        rooms = room_model.get_rooms(self.hotel_id)
        counts = {STATUS_AVAILABLE: 0, STATUS_OCCUPIED: 0, BOOKING_RESERVED: 0, STATUS_DIRTY: 0}

        # Group by floor
        floors = {}
        for r in rooms:
            f = r["floor"] or 1
            floors.setdefault(f, []).append(r)

        row = 0
        for floor in sorted(floors.keys()):
            # Floor header
            floor_lbl = QLabel(f"  Tầng {floor}")
            floor_lbl.setStyleSheet(
                "font-weight: bold; font-size: 13px; color: #00B4A6;"
                "background: #E0F7F5; border-radius: 8px; padding: 6px 12px;"
            )
            self.grid_layout.addWidget(floor_lbl, row, 0, 1, 8)
            row += 1

            col = 0
            for r in floors[floor]:
                ds = compute_room_display_status(r)
                counts[ds] = counts.get(ds, 0) + 1
                card = RoomCard(r, ds)
                card.clicked.connect(self._on_room_click)
                self.grid_layout.addWidget(card, row, col)
                col += 1
                if col >= 8:
                    col = 0
                    row += 1
            if col > 0:
                row += 1

        total = len(rooms)
        self.summary_lbl.setText(
            f"Tổng: {total} phòng  |  "
            f"🟢 Trống: {counts.get(STATUS_AVAILABLE,0)}  |  "
            f"🔴 Đang ở: {counts.get(STATUS_OCCUPIED,0)}  |  "
            f"🟡 Đã đặt: {counts.get(BOOKING_RESERVED,0)}  |  "
            f"⚫ Dọn dẹp: {counts.get(STATUS_DIRTY,0)}"
        )

    def _on_room_click(self, room: dict):
        dlg = RoomActionDialog(room, self.user, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh()



