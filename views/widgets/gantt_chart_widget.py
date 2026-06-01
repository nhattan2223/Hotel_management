import datetime

from PyQt6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

from views.widgets.gantt_canvas import GanttCanvas


class GanttChartWidget(QWidget):
    booking_clicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Controls
        ctrl = QHBoxLayout()
        from PyQt6.QtWidgets import QPushButton, QDateEdit
        from PyQt6.QtCore import QDate
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.dateChanged.connect(self._on_date_changed)

        self._days_combo = __import__("PyQt6.QtWidgets", fromlist=["QComboBox"]).QComboBox()
        for d in [14, 30, 60]:
            self._days_combo.addItem(f"{d} ngày", d)
        self._days_combo.setCurrentIndex(1)
        self._days_combo.currentIndexChanged.connect(self._on_date_changed)

        prev_btn = QPushButton("◀ Trước")
        prev_btn.setObjectName("SecondaryBtn")
        prev_btn.clicked.connect(self._go_prev)
        next_btn = QPushButton("Sau ▶")
        next_btn.setObjectName("SecondaryBtn")
        next_btn.clicked.connect(self._go_next)
        today_btn = QPushButton("Hôm nay")
        today_btn.setObjectName("PrimaryBtn")
        today_btn.clicked.connect(self._go_today)

        ctrl.addWidget(QLabel("Từ ngày:"))
        ctrl.addWidget(self._date_edit)
        ctrl.addWidget(QLabel("Hiển thị:"))
        ctrl.addWidget(self._days_combo)
        ctrl.addWidget(prev_btn)
        ctrl.addWidget(today_btn)
        ctrl.addWidget(next_btn)
        ctrl.addStretch()

        # Legend
        for color, label in [("#00B4A6", "Đang ở"), ("#F39C12", "Đã đặt"), ("#95A5A6", "Đã trả")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 16px;")
            ctrl.addWidget(dot)
            ctrl.addWidget(QLabel(label))

        layout.addLayout(ctrl)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(False)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._canvas = GanttCanvas()
        self._canvas.booking_clicked.connect(self._on_canvas_booking_clicked)
        self._scroll.setWidget(self._canvas)
        layout.addWidget(self._scroll)

        self._rooms = []
        self._bookings = []

    def set_data(self, rooms, bookings):
        self._rooms = rooms
        self._bookings = bookings
        self._refresh()

    def _refresh(self):
        qd = self._date_edit.date()
        start = datetime.date(qd.year(), qd.month(), qd.day())
        days = self._days_combo.currentData()
        self._canvas.set_data(self._rooms, self._bookings, start, days)

    def _on_date_changed(self):
        self._refresh()

    def _go_prev(self):
        days = self._days_combo.currentData()
        self._date_edit.setDate(self._date_edit.date().addDays(-days))

    def _go_next(self):
        days = self._days_combo.currentData()
        self._date_edit.setDate(self._date_edit.date().addDays(days))

    def _go_today(self):
        from PyQt6.QtCore import QDate
        self._date_edit.setDate(QDate.currentDate())

    def _on_canvas_booking_clicked(self, booking_id, room_id):
        # Explicitly forward the two-arg signal to avoid signature mismatches
        self.booking_clicked.emit(booking_id, room_id)

