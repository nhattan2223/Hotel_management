"""
ChefWindow — cửa sổ chính của role Bếp.
Tabs nằm ở:
  - menu_tab.py   : MenuManagementTab
  - order_tab.py  : OrderTab
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import pyqtSignal

from views.widgets.sidebar import SidebarWidget
from views.chef.menu.menu_tab import MenuManagementTab
from views.chef.order.order_tab import OrderTab


class ChefWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Bếp – {user['full_name']}")
        self.resize(1100, 720)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        nav_items = [
            ("menu",  "📋", "Thực đơn"),
            ("order", "🍽", "Đặt thực đơn"),
        ]
        self.sidebar = SidebarWidget(
            self.user.get("hotel_name", "Khách sạn"),
            f"Bếp: {self.user['full_name']}",
            nav_items,
            section_label="MENU CHỨC NĂNG",
        )
        self.sidebar.nav_clicked.connect(self._on_nav)
        self.sidebar.logout_clicked.connect(self.logout_requested)
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self._tabs = {
            "menu":  MenuManagementTab(self.user),
            "order": OrderTab(self.user),
        }
        for w in self._tabs.values():
            self.stack.addWidget(w)
        self._page_map = {k: i for i, k in enumerate(self._tabs)}

    def _on_nav(self, key):
        self.stack.setCurrentIndex(self._page_map.get(key, 0))
        w = self._tabs.get(key)
        if hasattr(w, "refresh"):
            w.refresh()
