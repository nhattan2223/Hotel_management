from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
)

from models import room_model, hotel_model


class RoomDialog(QDialog):
    def __init__(self, parent=None, room: dict = None):
        super().__init__(parent)
        self.room = room
        self.setWindowTitle("Thêm phòng" if not room else "Sửa phòng")
        self.setFixedWidth(380)
        self._setup_ui()
        if room:
            self._fill(room)

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.hotel_combo = QComboBox()
        self.hotels = hotel_model.get_all_hotels()
        for h in self.hotels:
            self.hotel_combo.addItem(h["name"], h["id"])

        self.type_combo = QComboBox()
        self.types = room_model.get_room_types()
        for t in self.types:
            self.type_combo.addItem(t["type_name"], t["id"])

        self.room_number = QLineEdit()
        self.floor = QSpinBox()
        self.floor.setRange(1, 50)

        layout.addRow("Chi nhánh:", self.hotel_combo)
        layout.addRow("Loại phòng:", self.type_combo)
        layout.addRow("Số phòng *:", self.room_number)
        layout.addRow("Tầng *:", self.floor)

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

    def _fill(self, r):
        for i, h in enumerate(self.hotels):
            if h["id"] == r["hotel_id"]:
                self.hotel_combo.setCurrentIndex(i)
        for i, t in enumerate(self.types):
            if t["type_name"] == r["type_name"]:
                self.type_combo.setCurrentIndex(i)
        self.room_number.setText(r["room_number"])
        self.floor.setValue(r["floor"] or 1)

    def _save(self):
        room_number = self.room_number.text().strip()
        if not room_number:
            QMessageBox.warning(self, "Lỗi", "Số phòng không được để trống.")
            return
        self.accept()

    def get_data(self):
        return {
            "hotel_id":    self.hotel_combo.currentData(),
            "type_id":     self.type_combo.currentData(),
            "room_number": self.room_number.text().strip(),
            "floor":       self.floor.value(),
        }


class RoomTypeDialog(QDialog):
    def __init__(self, parent=None, rtype: dict = None):
        super().__init__(parent)
        self.rtype = rtype
        self.setWindowTitle("Thêm loại phòng" if not rtype else "Sửa loại phòng")
        self.setFixedWidth(380)
        self._setup_ui()
        if rtype:
            self._fill(rtype)

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.type_name = QLineEdit()
        self.price = QDoubleSpinBox()
        self.price.setRange(0, 100_000_000)
        self.price.setSingleStep(50000)
        self.max_guest = QSpinBox()
        self.max_guest.setRange(1, 20)
        self.desc = QLineEdit()

        layout.addRow("Tên loại phòng *:", self.type_name)
        layout.addRow("Giá/đêm (đ):", self.price)
        layout.addRow("Tối đa khách:", self.max_guest)
        layout.addRow("Mô tả:", self.desc)

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

    def _fill(self, t):
        self.type_name.setText(t["type_name"])
        self.price.setValue(t["price_per_night"])
        self.max_guest.setValue(t["max_guest"])

    def _save(self):
        if not self.type_name.text().strip():
            QMessageBox.warning(self, "Lỗi", "Tên loại phòng không được để trống.")
            return
        try:
            if self.rtype:
                room_model.update_room_type(
                    self.rtype["id"],
                    self.type_name.text().strip(),
                    self.price.value(),
                    self.max_guest.value(),
                    self.desc.text().strip()
                )
            else:
                room_model.create_room_type(
                    self.type_name.text().strip(),
                    self.price.value(),
                    self.max_guest.value(),
                    self.desc.text().strip()
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

