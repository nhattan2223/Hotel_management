import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.init_db import init_db
from views.login_window import LoginWindow
from utils.config import ROLE_ADMIN, ROLE_RECEPTIONIST, ROLE_HOUSEKEEPING, ROLE_CHEF


def load_stylesheet(app: QApplication):
    qss_path = os.path.join(os.path.dirname(__file__), "resources", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


class App:
    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName("Hotel Management System")

        # Global font
        font = QFont("Segoe UI", 10)
        self.qt_app.setFont(font)

        load_stylesheet(self.qt_app)

        # Init DB
        init_db()

        self.login_win = None
        self.main_win  = None

    def show_login(self):
        if self.main_win:
            self.main_win.close()
            self.main_win = None

        self.login_win = LoginWindow()
        self.login_win.login_success.connect(self.on_login)
        self.login_win.show()

    def on_login(self, user: dict):
        self.login_win.close()
        role = user["role_name"]

        if role == ROLE_ADMIN:
            from views.admin.admin_window import AdminWindow
            win = AdminWindow(user)
        elif role == ROLE_RECEPTIONIST:
            from views.receptionist.receptionist_window import ReceptionistWindow
            win = ReceptionistWindow(user)
        elif role == ROLE_HOUSEKEEPING:
            from views.housekeeping.housekeeping_window import HousekeepingWindow
            win = HousekeepingWindow(user)
        elif role == ROLE_CHEF:
            from views.chef.chef_window import ChefWindow
            win = ChefWindow(user)
        else:
            self.show_login()
            return

        win.logout_requested.connect(self.show_login)
        self.main_win = win
        win.show()

    def run(self):
        self.show_login()
        sys.exit(self.qt_app.exec())


if __name__ == "__main__":
    App().run()
