from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLineEdit, QComboBox,
    QMessageBox, QPushButton,
)

from models import user_model, hotel_model


class UserDialog(QDialog):
    def __init__(self, parent=None, user: dict = None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Thêm nhân viên" if not user else "Sửa nhân viên")
        self.setFixedWidth(400)
        self._setup_ui()
        if user:
            self._fill(user)

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.username = QLineEdit()
        self.full_name = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.role_combo = QComboBox()
        self.roles = user_model.get_roles()
        for r in self.roles:
            self.role_combo.addItem(r["role_name"], r["id"])

        self.hotel_combo = QComboBox()
        self.hotels = hotel_model.get_all_hotels()
        for h in self.hotels:
            self.hotel_combo.addItem(h["name"], h["id"])

        layout.addRow("Tên đăng nhập *:", self.username)
        layout.addRow("Họ tên *:", self.full_name)
        layout.addRow("Điện thoại:", self.phone)
        layout.addRow("Email:", self.email)
        if not self.user:
            layout.addRow("Mật khẩu *:", self.password)
        layout.addRow("Vai trò:", self.role_combo)
        layout.addRow("Chi nhánh:", self.hotel_combo)

        btn_row = QHBoxLayout()
        save = QPushButton("Lưu")
        save.setObjectName("PrimaryBtn")
        save.clicked.connect(self._save)
        cancel = QPushButton("Hủy")
        cancel.setObjectName("SecondaryBtn")
        cancel.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        layout.addRow("", btn_row)

    def _fill(self, u):
        self.username.setText(u["username"])
        self.username.setReadOnly(True)
        self.full_name.setText(u["full_name"])
        self.phone.setText(u["phone"] or "")
        self.email.setText(u["email"] or "")
        for i, r in enumerate(self.roles):
            if r["role_name"] == u["role_name"]:
                self.role_combo.setCurrentIndex(i)
        for i, h in enumerate(self.hotels):
            if h["id"] == u["hotel_id"]:
                self.hotel_combo.setCurrentIndex(i)

    def _save(self):
        if not self.user and not self.password.text():
            QMessageBox.warning(self, "Lỗi", "Mật khẩu không được để trống.")
            return
        self.accept()

    def get_data(self):
        return {
            "username":  self.username.text().strip(),
            "password":  self.password.text() if not self.user else "—",
            "full_name": self.full_name.text().strip(),
            "phone":     self.phone.text().strip() or None,
            "email":     self.email.text().strip() or None,
            "role_id":   self.role_combo.currentData(),
            "hotel_id":  self.hotel_combo.currentData(),
        }
