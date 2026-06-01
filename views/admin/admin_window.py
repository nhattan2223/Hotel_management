from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QLabel, QStackedWidget, QApplication)
from PyQt6.QtCore import pyqtSignal, Qt
from views.widgets.sidebar import SidebarWidget
from views.admin.staff.staff_tab import StaffTab
from views.admin.statistics.statistics_tab import StatisticsTab
from views.admin.branch.branch_tab import BranchTab
from views.admin.rooms.rooms_tab import AdminRoomsTab


class AdminWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Admin – {user['full_name']}")
        self.resize(1280, 780)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        nav_items = [
            ("staff",      "👥", "Nhân viên"),
            ("stats",      "📊", "Thống kê"),
            ("branch",     "🏨", "Chi nhánh"),
            ("rooms",      "🛏", "Danh sách phòng"),
        ]
        self.sidebar = SidebarWidget("Hotel Admin", f"Xin chào, {self.user['full_name']}", nav_items)
        self.sidebar.nav_clicked.connect(self._on_nav)
        self.sidebar.logout_clicked.connect(self.logout_requested)
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea")
        layout.addWidget(self.stack)

        self._tabs = {
            "staff":  StaffTab(self.user),
            "stats":  StatisticsTab(self.user),
            "branch": BranchTab(self.user),
            "rooms":  AdminRoomsTab(self.user),
        }
        for w in self._tabs.values():
            self.stack.addWidget(w)

        self._page_map = {k: i for i, k in enumerate(self._tabs)}
        self.stack.setCurrentIndex(0)

    def _on_nav(self, key: str):
        idx = self._page_map.get(key, 0)
        self.stack.setCurrentIndex(idx)
        w = self._tabs.get(key)
        if hasattr(w, "refresh"):
            w.refresh()
