import re

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLineEdit, QMessageBox, QPushButton,
)


class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer: dict = None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Thêm khách hàng" if not customer else "Sửa khách hàng")
        self.setFixedWidth(400)
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.full_name = QLineEdit()
        self.id_card   = QLineEdit()
        self.phone     = QLineEdit()
        self.email     = QLineEdit()
        self.address   = QLineEdit()

        layout.addRow("Họ tên *:", self.full_name)
        layout.addRow("CCCD/Hộ chiếu:", self.id_card)
        layout.addRow("Điện thoại:", self.phone)
        layout.addRow("Email:", self.email)
        layout.addRow("Địa chỉ:", self.address)

        if customer:
            self.full_name.setText(customer["full_name"])
            self.id_card.setText(customer["id_card"] or "")
            self.phone.setText(customer["phone"] or "")
            self.email.setText(customer["email"] or "")
            self.address.setText(customer["address"] or "")

        btn_row = QHBoxLayout()
        ok = QPushButton("Lưu")
        ok.setObjectName("PrimaryBtn")
        ok.clicked.connect(self._save)
        cancel = QPushButton("Hủy")
        cancel.setObjectName("SecondaryBtn")
        cancel.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(ok)
        layout.addRow("", btn_row)

    def _save(self):
        name = self.full_name.text().strip()
        cccd = self.id_card.text().strip()
        phone = self.phone.text().strip()

        if not name:
            QMessageBox.warning(self, "Lỗi", "Họ tên không được để trống.")
            return

        if re.search(r'[0-9!@#\$%\^&\*()_\+=\[\]{};:"\\|,.<>\/?`~\-]', name):
            QMessageBox.warning(self, "Lỗi", "Họ tên không được chứa chữ số hoặc kí tự đặc biệt.")
            return

        if cccd and not re.match(r'^\d{12}$', cccd):
            QMessageBox.warning(self, "Lỗi", "CCCD phải gồm 12 chữ số, không chứa chữ cái, kí tự đặc biệt hoặc khoảng trống.")
            return

        if phone and not re.match(r'^0\d{9}$', phone):
            QMessageBox.warning(self, "Lỗi", "Số điện thoại phải gồm 10 chữ số, bắt đầu bằng số 0, không chứa chữ cái, kí tự đặc biệt hoặc khoảng trống.")
            return

        self.full_name.setText(name)
        self.id_card.setText(cccd)
        self.phone.setText(phone)
        self.accept()

    def get_data(self):
        return {
            "full_name": self.full_name.text().strip(),
            "id_card":   self.id_card.text().strip() or None,
            "phone":     self.phone.text().strip() or None,
            "email":     self.email.text().strip() or None,
            "address":   self.address.text().strip() or None,
        }
