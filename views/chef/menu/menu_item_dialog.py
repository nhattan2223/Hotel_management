from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QComboBox, QDoubleSpinBox,
    QLineEdit, QMessageBox, QPushButton,
)


class MenuItemDialog(QDialog):
    def __init__(self, meal_types: list, item: dict = None, parent=None):
        super().__init__(parent)
        self.item = item
        self.setWindowTitle("Thêm món" if not item else "Sửa món")
        self.setFixedWidth(360)
        self._meal_types = meal_types

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.meal_combo = QComboBox()
        for mt in meal_types:
            self.meal_combo.addItem(mt["name"], mt["id"])

        self.item_name = QLineEdit()
        self.price = QDoubleSpinBox()
        self.price.setRange(0, 10_000_000)
        self.price.setSingleStep(5_000)
        self.price.setSuffix(" đ")

        layout.addRow("Bữa:", self.meal_combo)
        layout.addRow("Tên món *:", self.item_name)
        layout.addRow("Giá:", self.price)

        if item:
            self.item_name.setText(item["item_name"])
            self.price.setValue(item["price"])
            for i, mt in enumerate(meal_types):
                if mt["id"] == item["meal_type_id"]:
                    self.meal_combo.setCurrentIndex(i)

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
        if not self.item_name.text().strip():
            QMessageBox.warning(self, "Lỗi", "Tên món không được để trống.")
            return
        self.accept()

    def get_data(self):
        return {
            "meal_type_id": self.meal_combo.currentData(),
            "item_name":    self.item_name.text().strip(),
            "price":        self.price.value(),
        }
