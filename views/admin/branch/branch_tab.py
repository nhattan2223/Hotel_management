from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QDialog, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from models import hotel_model
from views.admin.branch.hotel_dialog import HotelDialog


class BranchTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.current_user = user
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("🏨 Quản lý Chi nhánh")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        add_btn = QPushButton("+ Thêm chi nhánh")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.clicked.connect(self._add)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Tên khách sạn", "Địa chỉ", "Điện thoại", "Email", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        hotels = hotel_model.get_all_hotels()
        self.table.setRowCount(len(hotels))
        for i, h in enumerate(hotels):
            vals = [str(h["id"]), h["name"], h["address"],
                    h["phone"] or "—", h["email"] or "—"]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(4, 2, 4, 2)
            btn_l.setSpacing(6)
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("IconBtn")
            edit_btn.clicked.connect(lambda _, hid=h["id"]: self._edit(hid))
            del_btn = QPushButton("🗑")
            del_btn.setObjectName("IconBtn")
            del_btn.clicked.connect(lambda _, hid=h["id"]: self._delete(hid))
            btn_l.addWidget(edit_btn)
            btn_l.addWidget(del_btn)
            self.table.setCellWidget(i, 5, btn_w)
            self.table.setRowHeight(i, 40)

    def _add(self):
        dlg = HotelDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                hotel_model.create_hotel(**d)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _edit(self, hid):
        h = hotel_model.get_hotel(hid)
        if not h:
            return
        dlg = HotelDialog(self, h)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                hotel_model.update_hotel(hid, **d)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _delete(self, hid):
        r = QMessageBox.question(self, "Xác nhận", "Xóa chi nhánh này?")
        if r == QMessageBox.StandardButton.Yes:
            try:
                hotel_model.delete_hotel(hid)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa: {e}")



