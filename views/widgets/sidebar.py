from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class SidebarWidget(QWidget):
    """Reusable sidebar with nav buttons."""
    nav_clicked = pyqtSignal(str)
    logout_clicked = pyqtSignal()

    def __init__(self, title: str, subtitle: str, nav_items: list, section_label: str = "MENU CHỨC NĂNG", parent=None):
        """
        nav_items: list of (key, icon_text, label)
        """
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(254)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 18, 0, 16)
        layout.setSpacing(0)

        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(18, 0, 16, 14)
        brand_row.setSpacing(12)

        # Hotel icon placeholder
        icon_lbl = QLabel("🏨")
        icon_lbl.setText("▦")
        icon_lbl.setObjectName("SidebarIcon")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_row.addWidget(icon_lbl)

        t = QLabel(title)
        t.setObjectName("SidebarTitle")
        t.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        t.setWordWrap(True)
        brand_row.addWidget(t, 1)
        layout.addLayout(brand_row)

        s = QLabel(subtitle)
        s.setObjectName("SidebarSubtitle")
        s.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(s)

        # Divider
        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background: rgba(255,255,255,0.25); margin: 8px 16px;")
        layout.addWidget(div)
        layout.addSpacing(8)

        section = QLabel(section_label)
        section.setObjectName("SidebarSection")
        layout.addWidget(section)

        # Nav buttons
        self._buttons: dict[str, QPushButton] = {}
        for key, icon, label in nav_items:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._on_nav(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Logout
        logout_btn = QPushButton("  ↩  Đăng xuất")
        logout_btn.setObjectName("LogoutBtn")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout_clicked)
        layout.addWidget(logout_btn)

        # Select first by default
        if nav_items:
            first_key = nav_items[0][0]
            self._buttons[first_key].setChecked(True)

    def _on_nav(self, key: str):
        for k, btn in self._buttons.items():
            btn.setChecked(k == key)
        self.nav_clicked.emit(key)

    def set_active(self, key: str):
        self._on_nav(key)
