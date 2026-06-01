from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QFont
from utils.config import STATUS_AVAILABLE, STATUS_OCCUPIED, STATUS_DIRTY, BOOKING_RESERVED

STATUS_STYLES = {
    STATUS_AVAILABLE: ("#27AE60", "#FFFFFF"),
    STATUS_OCCUPIED:  ("#E74C3C", "#FFFFFF"),
    BOOKING_RESERVED: ("#F39C12", "#FFFFFF"),
    STATUS_DIRTY:     ("#95A5A6", "#FFFFFF"),
}

STATUS_LABELS = {
    STATUS_AVAILABLE: "Trống",
    STATUS_OCCUPIED:  "Đang ở",
    BOOKING_RESERVED: "Đã đặt",
    STATUS_DIRTY:     "Đang dọn",
}


class RoomCard(QWidget):
    clicked = pyqtSignal(dict)

    def __init__(self, room: dict, display_status: str, parent=None):
        super().__init__(parent)
        self.room = room
        self.display_status = display_status
        self.setFixedSize(120, 90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self):
        bg_color, _ = STATUS_STYLES.get(self.display_status, ("#95A5A6", "#FFF"))
        self.setToolTip(
            f"Phòng {self.room['room_number']}\n"
            f"Loại: {self.room['type_name']}\n"
            f"Giá: {int(self.room['price_per_night']):,} đ/đêm\n"
            f"Trạng thái: {STATUS_LABELS.get(self.display_status, self.display_status)}"
        )
        self.setStyleSheet(f"""
            RoomCard {{
                background-color: {bg_color};
                border-radius: 14px;
                border: 2px solid rgba(0,0,0,0.1);
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)

        num = QLabel(self.room["room_number"])
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent;")
        layout.addWidget(num)

        type_lbl = QLabel(self.room["type_name"])
        type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 10px; background: transparent;")
        layout.addWidget(type_lbl)

        status_lbl = QLabel(STATUS_LABELS.get(self.display_status, self.display_status))
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_lbl.setStyleSheet("""
            color: rgba(255,255,255,0.85);
            font-size: 10px;
            font-weight: bold;
            background: rgba(0,0,0,0.15);
            border-radius: 6px;
            padding: 2px 6px;
        """)
        layout.addWidget(status_lbl)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.room)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg_color, _ = STATUS_STYLES.get(self.display_status, ("#95A5A6", "#FFF"))
        path = QPainterPath()
        path.addRoundedRect(1, 1, self.width()-2, self.height()-2, 13, 13)
        painter.fillPath(path, QColor(bg_color))
        super().paintEvent(event)
