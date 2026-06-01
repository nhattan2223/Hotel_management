from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QStackedLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from models.user_model import authenticate


class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng nhập - Hotel Management")
        self.setFixedSize(1120, 700)
        self._setup_ui()

    def _setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)

        shell = QWidget()
        shell.setObjectName("LoginShell")
        shell.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        # ── Left panel với ảnh nền + overlay ──────────────────────────
        left = QFrame()
        left.setObjectName("LoginLeftPanel")
        left.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        stack = QStackedLayout(left)
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # Overlay tối phủ lên ảnh nền
        overlay = QWidget()
        overlay.setObjectName("LoginOverlay")
        overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        stack.addWidget(overlay)

        # Content widget bên trên overlay
        content_widget = QWidget()
        content_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        left_layout = QVBoxLayout(content_widget)
        left_layout.setContentsMargins(64, 54, 58, 54)
        left_layout.setSpacing(0)
        stack.addWidget(content_widget)
        stack.setCurrentIndex(1)

        # Brand row
        brand_row = QHBoxLayout()
        brand_row.setSpacing(14)
        brand_icon = QLabel("▦")
        brand_icon.setObjectName("LoginBrandIcon")
        brand_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_row.addWidget(brand_icon)

        brand_name = QLabel("Grand Hotel")
        brand_name.setObjectName("LoginBrandName")
        brand_row.addWidget(brand_name)
        brand_row.addStretch()
        left_layout.addLayout(brand_row)
        left_layout.addSpacing(100)

        eyebrow = QLabel("HỆ THỐNG QUẢN LÝ KHÁCH SẠN")
        eyebrow.setObjectName("LoginEyebrow")
        left_layout.addWidget(eyebrow)

        hero_title = QLabel("Quản lý thông minh\nVận hành hiệu quả")
        hero_title.setObjectName("LoginHeroTitle")
        left_layout.addWidget(hero_title)

        hero_desc = QLabel(
            "Giải pháp toàn diện giúp bạn quản lý khách sạn,\n"
            "tối ưu doanh thu và nâng cao trải nghiệm khách hàng."
        )
        hero_desc.setObjectName("LoginHeroDesc")
        left_layout.addWidget(hero_desc)

        left_layout.addStretch(1)

        # ── Right panel ───────────────────────────────────────────────
        right = QFrame()
        right.setObjectName("LoginRightPanel")
        right.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(70, 60, 70, 60)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("LoginCard")
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(34, 34, 34, 34)
        card_layout.setSpacing(12)

        icon_lbl = QLabel("▦")
        icon_lbl.setObjectName("LoginIcon")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Đăng nhập hệ thống")
        title.setObjectName("LoginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        sub = QLabel("Vui lòng đăng nhập để tiếp tục sử dụng")
        sub.setObjectName("LoginSubtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(sub)
        card_layout.addSpacing(22)

        user_label = QLabel("Tài khoản")
        user_label.setObjectName("FieldLabel")
        card_layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setObjectName("LoginInput")
        self.username_input.setMinimumHeight(48)
        self.username_input.setPlaceholderText("Nhập tài khoản")
        card_layout.addWidget(self.username_input)
        card_layout.addSpacing(8)

        pass_label = QLabel("Mật khẩu")
        pass_label.setObjectName("FieldLabel")
        card_layout.addWidget(pass_label)

        self.password_input = QLineEdit()
        self.password_input.setObjectName("LoginInput")
        self.password_input.setMinimumHeight(48)
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._do_login)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(10)

        self.error_lbl = QLabel("")
        self.error_lbl.setObjectName("LoginError")
        self.error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.error_lbl)

        login_btn = QPushButton("Đăng nhập")
        login_btn.setObjectName("PrimaryBtn")
        login_btn.setFixedHeight(48)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self._do_login)
        card_layout.addWidget(login_btn)

        right_layout.addWidget(card)

        shell_layout.addWidget(left, 3)
        shell_layout.addWidget(right, 2)
        main.addWidget(shell)

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.error_lbl.setText("Vui lòng nhập tài khoản và mật khẩu.")
            return

        user = authenticate(username, password)
        if user:
            self.login_success.emit(user)
        else:
            self.error_lbl.setText("Tài khoản hoặc mật khẩu không đúng.")
            self.password_input.clear()