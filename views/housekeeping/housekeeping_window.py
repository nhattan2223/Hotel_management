from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

from views.widgets.sidebar import SidebarWidget
from views.housekeeping.housekeeping_tab import HousekeepingRoomsTab


class HousekeepingWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.hotel_id = user["hotel_id"]
        self.setWindowTitle(f"Buồng phòng – {user['full_name']}")
        self.resize(1100, 720)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        nav_items = [("rooms", "🛏", "Danh sách phòng")]
        self.sidebar = SidebarWidget(
            self.user.get("hotel_name", "Khách sạn"),
            f"Buồng phòng: {self.user['full_name']}",
            nav_items
        )
        self.sidebar.logout_clicked.connect(self.logout_requested)
        layout.addWidget(self.sidebar)

        self.rooms_tab = HousekeepingRoomsTab(self.user)
        layout.addWidget(self.rooms_tab)
