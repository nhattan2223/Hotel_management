from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLineEdit, QMessageBox, QPushButton,
)


class HotelDialog(QDialog):
    def __init__(self, parent=None, hotel: dict = None):
        super().__init__(parent)
        self.hotel = hotel
        self.setWindowTitle("Thêm chi nhánh" if not hotel else "Sửa chi nhánh")
        self.setFixedWidth(420)
        self._setup_ui()
        if hotel:
            self._fill(hotel)

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.name = QLineEdit()
        self.address = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()

        layout.addRow("Tên khách sạn *:", self.name)
        layout.addRow("Địa chỉ *:", self.address)
        layout.addRow("Điện thoại:", self.phone)
        layout.addRow("Email:", self.email)

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

    def _fill(self, h):
        self.name.setText(h["name"])
        self.address.setText(h["address"])
        self.phone.setText(h["phone"] or "")
        self.email.setText(h["email"] or "")

    def _save(self):
        if not self.name.text().strip() or not self.address.text().strip():
            QMessageBox.warning(self, "Lỗi", "Tên và địa chỉ không được để trống.")
            return
        self.accept()

    def get_data(self):
        return {
            "name":    self.name.text().strip(),
            "address": self.address.text().strip(),
            "phone":   self.phone.text().strip() or None,
            "email":   self.email.text().strip() or None,
        }
