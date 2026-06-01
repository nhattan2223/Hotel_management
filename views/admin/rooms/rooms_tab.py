from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QDialog, QMessageBox, QComboBox,
                              QHeaderView, QTabWidget)
from PyQt6.QtCore import Qt
from utils.config import (BOOKING_STATUS_VN, BOOKING_STATUS_COLOR, ROOM_STATUS_VN,
                          STATUS_DIRTY)
from models import room_model, hotel_model
from views.admin.rooms.room_dialogs import RoomDialog, RoomTypeDialog


class AdminRoomsTab(QWidget):
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
        title = QLabel("🛏 Danh sách Phòng")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()

        hdr.addWidget(QLabel("Chi nhánh:"))
        self.hotel_combo = QComboBox()
        self.hotels = hotel_model.get_all_hotels()
        self.hotel_combo.addItem("Tất cả", None)
        for h in self.hotels:
            self.hotel_combo.addItem(h["name"], h["id"])
        self.hotel_combo.currentIndexChanged.connect(self.refresh)
        hdr.addWidget(self.hotel_combo)

        add_room_btn = QPushButton("+ Thêm phòng")
        add_room_btn.setObjectName("PrimaryBtn")
        add_room_btn.clicked.connect(self._add_room)
        hdr.addWidget(add_room_btn)

        add_type_btn = QPushButton("+ Loại phòng")
        add_type_btn.setObjectName("SecondaryBtn")
        add_type_btn.clicked.connect(self._manage_types)
        hdr.addWidget(add_type_btn)

        layout.addLayout(hdr)

        tabs = QTabWidget()

        # Rooms tab
        rooms_w = QWidget()
        rooms_l = QVBoxLayout(rooms_w)
        rooms_l.setContentsMargins(0, 12, 0, 0)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Chi nhánh", "Phòng", "Tầng", "Loại phòng", "Giá/đêm", "Trạng thái", "Thao tác"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        rooms_l.addWidget(self.table)
        tabs.addTab(rooms_w, "Phòng")

        # Room types tab
        types_w = QWidget()
        types_l = QVBoxLayout(types_w)
        types_l.setContentsMargins(0, 12, 0, 0)
        self.types_table = QTableWidget()
        self.types_table.setColumnCount(5)
        self.types_table.setHorizontalHeaderLabels(
            ["ID", "Loại phòng", "Giá/đêm", "Tối đa khách", "Thao tác"]
        )
        self.types_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.types_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.types_table.setAlternatingRowColors(True)
        self.types_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        types_l.addWidget(self.types_table)
        tabs.addTab(types_w, "Loại phòng")

        layout.addWidget(tabs)

    def refresh(self):
        hotel_id = self.hotel_combo.currentData()
        rooms = room_model.get_rooms(hotel_id)
        self.table.setRowCount(len(rooms))
        STATUS_VN = BOOKING_STATUS_VN
        for i, r in enumerate(rooms):
            status_display = r["occupancy_status"]
            if r["housekeeping"] == STATUS_DIRTY:
                status_display = STATUS_DIRTY
            vals = [str(r["id"]), r["hotel_name"], r["room_number"],
                    str(r["floor"] or "—"), r["type_name"],
                    f"{int(r['price_per_night']):,} đ",
                    STATUS_VN.get(status_display, status_display)]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(4, 2, 4, 2)
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("IconBtn")
            edit_btn.clicked.connect(lambda _, rid=r["id"]: self._edit_room(rid))
            del_btn = QPushButton("🗑")
            del_btn.setObjectName("IconBtn")
            del_btn.clicked.connect(lambda _, rid=r["id"]: self._delete_room(rid))
            btn_l.addWidget(edit_btn)
            btn_l.addWidget(del_btn)
            self.table.setCellWidget(i, 7, btn_w)
            self.table.setRowHeight(i, 40)

        # Room types
        types = room_model.get_room_types()
        self.types_table.setRowCount(len(types))
        for i, t in enumerate(types):
            vals = [str(t["id"]), t["type_name"],
                    f"{int(t['price_per_night']):,} đ", str(t["max_guest"])]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.types_table.setItem(i, j, item)
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(4, 2, 4, 2)
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("IconBtn")
            edit_btn.clicked.connect(lambda _, tid=t["id"]: self._edit_type(tid))
            btn_l.addWidget(edit_btn)
            self.types_table.setCellWidget(i, 4, btn_w)
            self.types_table.setRowHeight(i, 40)

    def _add_room(self):
        dlg = RoomDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                room_model.create_room(**d)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _edit_room(self, rid):
        rooms = room_model.get_rooms()
        r = next((x for x in rooms if x["id"] == rid), None)
        if not r:
            return
        dlg = RoomDialog(self, r)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                room_model.update_room(rid, d["type_id"], d["room_number"], d["floor"])
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _delete_room(self, rid):
        r = QMessageBox.question(self, "Xác nhận", "Xóa phòng này?")
        if r == QMessageBox.StandardButton.Yes:
            try:
                room_model.delete_room(rid)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa: {e}")

    def _manage_types(self):
        dlg = RoomTypeDialog(self)
        dlg.exec()
        self.refresh()

    def _edit_type(self, tid):
        types = room_model.get_room_types()
        t = next((x for x in types if x["id"] == tid), None)
        if not t:
            return
        dlg = RoomTypeDialog(self, t)
        dlg.exec()
        self.refresh()
