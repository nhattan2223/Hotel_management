"""
Dialog tách ra từ service_tab.py:
  - AddServiceOrderDialog  : chọn dịch vụ + số lượng cho booking
  - ServiceDialog          : thêm / sửa dịch vụ trong danh mục
"""
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QMessageBox, QCheckBox,
)

_FIXED_QTY_KEYWORDS = ["giặt ủi", "spa", "thuê phòng hội nghị", "thuê xe máy", "đưa đón sân bay"]


class AddServiceOrderDialog(QDialog):
    """Chọn dịch vụ + số lượng, hiển thị giá live."""

    def __init__(self, services: list, parent=None):
        super().__init__(parent)
        self._services = services
        self.setWindowTitle("Thêm dịch vụ cho booking")
        self.setFixedWidth(420)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        self.svc_combo = QComboBox()
        for s in self._services:
            stock = f"  (còn {s['stocking']})" if s["stocking"] is not None else ""
            self.svc_combo.addItem(
                f"{s['service_name']}  –  {int(s['price']):,} đ{stock}", s["id"]
            )
        self.svc_combo.currentIndexChanged.connect(self._refresh_preview)
        layout.addRow("Dịch vụ:", self.svc_combo)

        self.price_lbl = QLabel()
        self.price_lbl.setStyleSheet("color:#00B4A6;font-weight:bold;font-size:14px;")
        layout.addRow("Đơn giá:", self.price_lbl)

        self.qty = QSpinBox()
        self.qty.setRange(1, 999)
        self.qty.valueChanged.connect(self._refresh_preview)
        layout.addRow("Số lượng:", self.qty)

        self.total_lbl = QLabel()
        self.total_lbl.setStyleSheet("font-size:15px;font-weight:bold;color:#1A2E35;")
        layout.addRow("Thành tiền:", self.total_lbl)

        self._refresh_preview()

        btn_row = QHBoxLayout()
        ok = QPushButton("✅ Thêm vào dịch vụ")
        ok.setObjectName("PrimaryBtn")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Hủy")
        cancel.setObjectName("SecondaryBtn")
        cancel.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(ok)
        layout.addRow("", btn_row)

    def _current_svc(self) -> dict | None:
        sid = self.svc_combo.currentData()
        return next((s for s in self._services if s["id"] == sid), None)

    def _refresh_preview(self):
        s = self._current_svc()
        if not s:
            return
        self.price_lbl.setText(f"{int(s['price']):,} đ")
        is_fixed = any(k in s["service_name"].lower() for k in _FIXED_QTY_KEYWORDS)
        if is_fixed:
            self.qty.blockSignals(True)
            self.qty.setValue(1)
            self.qty.setEnabled(False)
            self.qty.blockSignals(False)
        else:
            self.qty.setEnabled(True)
        self.total_lbl.setText(f"{int(s['price'] * self.qty.value()):,} đ")

    def get_data(self) -> tuple:
        s = self._current_svc()
        if not s:
            raise ValueError("Không tìm thấy dịch vụ.")
        return s["id"], self.qty.value(), s["price"]


class ServiceDialog(QDialog):
    """Thêm mới / Chỉnh sửa dịch vụ trong danh mục."""

    def __init__(self, service: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm dịch vụ mới" if not service else "Sửa dịch vụ")
        self.setFixedWidth(380)
        self._setup_ui()
        if service:
            self._fill(service)

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Ví dụ: Giặt ủi, Spa massage…")

        self.price = QDoubleSpinBox()
        self.price.setRange(0, 50_000_000)
        self.price.setSingleStep(10_000)
        self.price.setDecimals(0)
        self.price.setSuffix(" đ")

        self.unlimited_cb = QCheckBox("Không giới hạn")
        self.unlimited_cb.setChecked(True)
        self.unlimited_cb.stateChanged.connect(self._on_unlimited_changed)

        self.stocking = QSpinBox()
        self.stocking.setRange(0, 9999)
        self.stocking.setEnabled(False)

        layout.addRow("Tên dịch vụ *:", self.name)
        layout.addRow("Giá:", self.price)
        layout.addRow("Tồn kho:", self.unlimited_cb)
        layout.addRow("Số lượng:", self.stocking)

        btn_row = QHBoxLayout()
        ok = QPushButton("💾 Lưu")
        ok.setObjectName("PrimaryBtn")
        ok.clicked.connect(self._save)
        cancel = QPushButton("Hủy")
        cancel.setObjectName("SecondaryBtn")
        cancel.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(ok)
        layout.addRow("", btn_row)

    def _on_unlimited_changed(self):
        unlimited = self.unlimited_cb.isChecked()
        self.stocking.setEnabled(not unlimited)
        if unlimited:
            self.stocking.setValue(0)

    def _fill(self, s: dict):
        self.name.setText(s["service_name"])
        self.price.setValue(s["price"])
        is_unlimited = s["stocking"] is None
        self.unlimited_cb.setChecked(is_unlimited)
        self.stocking.setValue(0 if is_unlimited else s["stocking"])
        self.stocking.setEnabled(not is_unlimited)

    def _save(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Lỗi", "Tên dịch vụ không được để trống.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "stocking": None if self.unlimited_cb.isChecked() else self.stocking.value(),
            "name":     self.name.text().strip(),
            "price":    self.price.value(),
        }
