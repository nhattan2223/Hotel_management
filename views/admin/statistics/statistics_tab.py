import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QTableWidget,
                              QHeaderView, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models import invoice_model, hotel_model
from views.admin.statistics.statistics_charts import draw_revenue, draw_occupancy, draw_top


class StatisticsTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.current_user = user
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header + filters
        hdr = QHBoxLayout()
        title = QLabel("📊 Thống kê")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()

        hdr.addWidget(QLabel("Chi nhánh:"))
        self.hotel_combo = QComboBox()
        self.hotels = hotel_model.get_all_hotels()
        self.hotel_combo.addItem("Tất cả", None)
        for h in self.hotels:
            self.hotel_combo.addItem(h["name"], h["id"])
        self.hotel_combo.currentIndexChanged.connect(self.refresh)
        hdr.addWidget(self.hotel_combo)

        hdr.addWidget(QLabel("Năm:"))
        self.year_combo = QComboBox()
        cur_year = datetime.date.today().year
        for y in range(cur_year - 2, cur_year + 1):
            self.year_combo.addItem(str(y), y)
        self.year_combo.setCurrentIndex(self.year_combo.count() - 1)
        self.year_combo.currentIndexChanged.connect(self.refresh)
        hdr.addWidget(self.year_combo)

        hdr.addWidget(QLabel("Tháng:"))
        self.month_combo = QComboBox()
        self.month_combo.addItem("Cả năm", None)
        for m in range(1, 13):
            self.month_combo.addItem(f"Tháng {m}", m)
        self.month_combo.setCurrentIndex(datetime.date.today().month)
        self.month_combo.currentIndexChanged.connect(self.refresh)
        hdr.addWidget(self.month_combo)

        layout.addLayout(hdr)

        # Stat cards row
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(16)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.cards_layout)

        # Charts area
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        # Revenue chart
        rev_frame = QFrame()
        rev_frame.setObjectName("Card")
        rev_layout = QVBoxLayout(rev_frame)
        self.rev_title = QLabel("Doanh thu")
        self.rev_title.setObjectName("SectionHeader")
        rev_layout.addWidget(self.rev_title)
        self.rev_fig = Figure(figsize=(6, 3), facecolor="white")
        self.rev_canvas = FigureCanvas(self.rev_fig)
        self.rev_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        rev_layout.addWidget(self.rev_canvas)
        rev_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        charts_row.addWidget(rev_frame, 3)

        # Occupancy pie
        occ_frame = QFrame()
        occ_frame.setObjectName("Card")
        occ_layout = QVBoxLayout(occ_frame)
        occ_title = QLabel("Tỷ lệ lấp đầy")
        occ_title.setObjectName("SectionHeader")
        occ_layout.addWidget(occ_title)
        self.occ_fig = Figure(figsize=(3, 3), facecolor="white")
        self.occ_canvas = FigureCanvas(self.occ_fig)
        self.occ_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        occ_layout.addWidget(self.occ_canvas)
        occ_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        charts_row.addWidget(occ_frame, 2)

        layout.addLayout(charts_row)

        # Top customers
        top_frame = QFrame()
        top_frame.setObjectName("Card")
        top_layout = QVBoxLayout(top_frame)
        top_title = QLabel("🏆 Top khách hàng")
        top_title.setObjectName("SectionHeader")
        top_layout.addWidget(top_title)
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(4)
        self.top_table.setHorizontalHeaderLabels(["Họ tên", "SĐT", "Số lần ở", "Tổng chi tiêu"])
        self.top_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.top_table.setMaximumHeight(200)
        self.top_table.setAlternatingRowColors(True)
        self.top_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        top_layout.addWidget(self.top_table)
        layout.addWidget(top_frame)

    def refresh(self):
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        hotel_id = self.hotel_combo.currentData()

        draw_revenue(self, hotel_id, year, month)
        draw_occupancy(self, hotel_id)
        draw_top(self, hotel_id)
