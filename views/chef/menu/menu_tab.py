"""
MenuManagementTab — quản lý thực đơn cho Chef.
Dialog thêm/sửa món nằm ở menu_item_dialog.py
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QComboBox, QMessageBox,
)
from PyQt6.QtCore import Qt
from models import menu_model
from views.chef.menu.menu_item_dialog import MenuItemDialog


class MenuManagementTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("📋 Quản lý Thực đơn")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        add_btn = QPushButton("+ Thêm món")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.clicked.connect(self._add_item)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Lọc theo bữa:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Tất cả", None)
        self._meal_types = menu_model.get_meal_types()
        for mt in self._meal_types:
            self.filter_combo.addItem(mt["name"], mt["id"])
        self.filter_combo.currentIndexChanged.connect(self.refresh)
        filter_row.addWidget(self.filter_combo)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Bữa", "Tên món", "Giá (đ)", "Kích hoạt", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        mt_id = self.filter_combo.currentData()
        items = menu_model.get_menu_items(mt_id, active_only=False)
        self.table.setRowCount(len(items))
        for i, item in enumerate(items):
            vals = [
                str(item["id"]), item["meal_type_name"], item["item_name"],
                f"{int(item['price']):,}",
                "✅ Có" if item["is_active"] else "❌ Không",
            ]
            for j, v in enumerate(vals):
                itm = QTableWidgetItem(v)
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, itm)

            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(4, 2, 4, 2)
            btn_l.setSpacing(4)
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("IconBtn")
            edit_btn.clicked.connect(lambda _, mid=item["id"]: self._edit_item(mid))
            toggle_btn = QPushButton("🔄")
            toggle_btn.setObjectName("IconBtn")
            toggle_btn.setToolTip("Bật/tắt")
            toggle_btn.clicked.connect(
                lambda _, mid=item["id"], act=item["is_active"]: self._toggle(mid, act)
            )
            btn_l.addWidget(edit_btn)
            btn_l.addWidget(toggle_btn)
            self.table.setCellWidget(i, 5, btn_w)
            self.table.setRowHeight(i, 40)

    def _add_item(self):
        dlg = MenuItemDialog(self._meal_types, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                menu_model.create_menu_item(d["meal_type_id"], d["item_name"], d["price"])
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _edit_item(self, mid):
        items = menu_model.get_menu_items(active_only=False)
        item = next((x for x in items if x["id"] == mid), None)
        if not item:
            return
        dlg = MenuItemDialog(self._meal_types, item, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            menu_model.update_menu_item(mid, d["meal_type_id"], d["item_name"],
                                        d["price"], item["is_active"])
            self.refresh()

    def _toggle(self, mid, current_active):
        items = menu_model.get_menu_items(active_only=False)
        item = next((x for x in items if x["id"] == mid), None)
        if item:
            menu_model.update_menu_item(
                mid, item["meal_type_id"], item["item_name"],
                item["price"], 0 if current_active else 1,
            )
            self.refresh()



