from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer

from models import room_model
from utils.config import STATUS_DIRTY, STATUS_OCCUPIED, STATUS_CLEAN, BOOKING_RESERVED
from services.booking_service import compute_room_display_status


class HousekeepingRoomsTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self.hotel_id = user["hotel_id"]
        self._setup_ui()
        self.refresh()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(20_000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("🧹 Quản lý Buồng phòng")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        sub = QLabel("Click vào phòng Sạch để đánh dấu Cần dọn, click phòng Cần dọn để đánh dấu Sạch")
        sub.setObjectName("PageSubtitle")
        hdr.addStretch()
        hdr.addWidget(sub)
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.setObjectName("SecondaryBtn")
        refresh_btn.clicked.connect(self.refresh)
        hdr.addWidget(refresh_btn)
        layout.addLayout(hdr)

        legend = QHBoxLayout()
        legend.addWidget(QLabel("Chú thích:"))
        for color, label in [("#27AE60","Trống – Sạch"), ("#E74C3C","Đang ở"),
                              ("#F39C12","Đã đặt – Sạch"), ("#95A5A6","Cần dọn dẹp")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 18px;")
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #4A6572; font-size: 12px; margin-right: 12px;")
            legend.addWidget(dot)
            legend.addWidget(lbl)
        legend.addStretch()
        layout.addLayout(legend)

        note = QLabel("⚠️  Buồng phòng có thể chuyển đổi giữa trạng thái Sạch và Cần dọn. Phòng Đang ở sẽ không thể thay đổi.")
        note.setStyleSheet(
            "background: #FEF3DC; color: #8B6914; border-radius: 8px;"
            "padding: 8px 12px; font-size: 12px;"
        )
        layout.addWidget(note)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

        self.summary_lbl = QLabel()
        self.summary_lbl.setStyleSheet("color: #4A6572; font-size: 12px;")
        layout.addWidget(self.summary_lbl)

    def refresh(self):
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        rooms = room_model.get_rooms(self.hotel_id)
        dirty_count = 0
        clean_count = 0

        floors = {}
        for r in rooms:
            f = r["floor"] or 1
            floors.setdefault(f, []).append(r)

        row = 0
        for floor in sorted(floors.keys()):
            floor_lbl = QLabel(f"  Tầng {floor}")
            floor_lbl.setStyleSheet(
                "font-weight: bold; font-size: 13px; color: #00B4A6;"
                "background: #E0F7F5; border-radius: 8px; padding: 6px 12px;"
            )
            self.grid_layout.addWidget(floor_lbl, row, 0, 1, 8)
            row += 1

            col = 0
            for r_data in floors[floor]:
                card = self._make_room_card(r_data)
                self.grid_layout.addWidget(card, row, col)
                if r_data["housekeeping"] == STATUS_DIRTY:
                    dirty_count += 1
                else:
                    clean_count += 1
                col += 1
                if col >= 8:
                    col = 0
                    row += 1
            if col > 0:
                row += 1

        self.summary_lbl.setText(
            f"⚫ Cần dọn: {dirty_count}  |  ✅ Đã sạch: {clean_count}"
        )

    def _make_room_card(self, room: dict) -> QFrame:
        is_dirty = (room["housekeeping"] == STATUS_DIRTY)
        is_occupied = (room["occupancy_status"] == STATUS_OCCUPIED)

        display_status = compute_room_display_status(room)

        if is_dirty:
            bg = "#95A5A6"
            status_text = "Cần dọn 🧹"
        elif is_occupied:
            bg = "#E74C3C"
            status_text = "Đang ở"
        elif display_status == BOOKING_RESERVED:
            bg = "#F39C12"
            status_text = "Đã đặt – Sạch"
        else:
            bg = "#27AE60"
            status_text = "Sạch"

        card = QFrame()
        card.setFixedSize(128, 96)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 14px;
                border: 2px solid rgba(0,0,0,0.1);
            }}
        """)

        if is_occupied:
            card.setCursor(Qt.CursorShape.ArrowCursor)
            card.setToolTip(
                f"Phòng {room['room_number']}\n"
                f"Loại: {room['type_name']}\n"
                f"Trạng thái: Đang ở\n"
                f"Không thể thay đổi trạng thái phòng đang có khách."
            )
        else:
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.setToolTip(
                f"Phòng {room['room_number']}\n"
                f"Loại: {room['type_name']}\n"
                f"Vệ sinh: {'Cần dọn' if is_dirty else 'Sạch'}\n"
                f"Click để {'đánh dấu sạch' if is_dirty else 'đánh dấu cần dọn'}"
            )

        v = QVBoxLayout(card)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(2)

        num = QLabel(room["room_number"])
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent;")
        v.addWidget(num)

        type_lbl = QLabel(room["type_name"])
        type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 10px; background: transparent;")
        v.addWidget(type_lbl)

        st_lbl = QLabel(status_text)
        st_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st_lbl.setStyleSheet("""
            color: rgba(255,255,255,0.9);
            font-size: 10px; font-weight: bold;
            background: rgba(0,0,0,0.15);
            border-radius: 6px; padding: 2px 6px;
        """)
        v.addWidget(st_lbl)

        if not is_occupied:
            card.mousePressEvent = lambda e, rid=room["id"], dirty=is_dirty: self._toggle_clean(rid, dirty)
        return card

    def _toggle_clean(self, room_id: int, is_dirty: bool):
        if is_dirty:
            r = QMessageBox.question(
                self, "Xác nhận",
                "Đánh dấu phòng này là ĐÃ DỌN SẠCH?\n"
                "Lễ tân sẽ thấy trạng thái thực tế của phòng."
            )
            if r == QMessageBox.StandardButton.Yes:
                room_model.set_housekeeping_status(room_id, STATUS_CLEAN)
                self.refresh()
        else:
            r = QMessageBox.question(
                self, "Xác nhận",
                "Đánh dấu phòng này là CẦN DỌN?\n"
                "Lễ tân sẽ thấy phòng cần dọn dẹp."
            )
            if r == QMessageBox.StandardButton.Yes:
                room_model.set_housekeeping_status(room_id, STATUS_DIRTY)
                self.refresh()
