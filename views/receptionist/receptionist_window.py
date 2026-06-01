from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import pyqtSignal
from views.widgets.sidebar import SidebarWidget
from views.receptionist.rooms.rooms_tab import ReceptionRoomsTab
from views.receptionist.booking.booking_tab import BookingTab
from views.receptionist.gantt.gantt_tab import GanttTab
from views.receptionist.service.service_tab import ServiceTab
from views.receptionist.customer.customer_tab import CustomerTab
from views.receptionist.invoice.invoice_tab import InvoiceTab


class ReceptionistWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Lễ tân – {user['full_name']}")
        self.resize(1280, 780)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        nav_items = [
            ("rooms",    "🛏", "Danh sách phòng"),
            ("gantt",    "📅", "Lịch đặt phòng"),
            ("booking",  "📋", "Đặt / Sửa booking"),
            ("service",  "🛎", "Dịch vụ"),
            ("invoice",  "🧾", "Hóa đơn"),
            ("customer", "👤", "Khách hàng"),
        ]
        self.sidebar = SidebarWidget(
            self.user.get("hotel_name", "Khách sạn"),
            f"Lễ tân: {self.user['full_name']}",
            nav_items
        )
        self.sidebar.nav_clicked.connect(self._on_nav)
        self.sidebar.logout_clicked.connect(self.logout_requested)
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        hotel_id = self.user["hotel_id"]
        self._tabs = {
            "rooms":    ReceptionRoomsTab(self.user),
            "gantt":    GanttTab(self.user),
            "booking":  BookingTab(self.user),
            "service":  ServiceTab(self.user),
            "invoice":  InvoiceTab(self.user),
            "customer": CustomerTab(self.user),
        }
        for w in self._tabs.values():
            self.stack.addWidget(w)

        self._page_map = {k: i for i, k in enumerate(self._tabs)}

    def _on_nav(self, key: str):
        idx = self._page_map.get(key, 0)
        self.stack.setCurrentIndex(idx)
        w = self._tabs.get(key)
        if hasattr(w, "refresh"):
            w.refresh()
