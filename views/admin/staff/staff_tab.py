from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QDialog, QLineEdit, QComboBox,
                              QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from models import user_model, hotel_model
from views.admin.staff.user_dialog import UserDialog


class StaffTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.current_user = user
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("👥 Quản lý Nhân viên")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()

        # Role filter
        hdr.addWidget(QLabel("Vai trò:"))
        self.role_filter = QComboBox()
        self.role_filter.addItem("Tất cả", None)
        for r in user_model.get_roles():
            self.role_filter.addItem(r["role_name"], r["id"])
        self.role_filter.currentIndexChanged.connect(self.refresh)
        hdr.addWidget(self.role_filter)

        # Hotel / Branch filter
        hdr.addWidget(QLabel("Chi nhánh:"))
        self.hotel_filter = QComboBox()
        self.hotel_filter.addItem("Tất cả", None)
        for h in hotel_model.get_all_hotels():
            self.hotel_filter.addItem(h["name"], h["id"])
        self.hotel_filter.currentIndexChanged.connect(self.refresh)
        hdr.addWidget(self.hotel_filter)

        add_btn = QPushButton("+ Thêm nhân viên")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.clicked.connect(self._add_user)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Tên đăng nhập", "Họ tên", "Điện thoại", "Email", "Vai trò", "Chi nhánh", "Thao tác"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def refresh(self):
        role_id = self.role_filter.currentData()
        hotel_id = self.hotel_filter.currentData()
        users = user_model.get_all_users(hotel_id=hotel_id)
        if role_id:
            users = [u for u in users if u["role_id"] == role_id]
        self.table.setRowCount(len(users))
        for i, u in enumerate(users):
            vals = [str(u["id"]), u["username"], u["full_name"],
                    u["phone"] or "—", u["email"] or "—",
                    u["role_name"], u["hotel_name"]]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)
            # Action buttons
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(4, 2, 4, 2)
            btn_l.setSpacing(6)
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("IconBtn")
            edit_btn.setToolTip("Chỉnh sửa")
            edit_btn.clicked.connect(lambda _, uid=u["id"]: self._edit_user(uid))
            del_btn = QPushButton("🗑")
            del_btn.setObjectName("IconBtn")
            del_btn.setToolTip("Vô hiệu hóa")
            del_btn.clicked.connect(lambda _, uid=u["id"]: self._delete_user(uid))
            pw_btn = QPushButton("🔑")
            pw_btn.setObjectName("IconBtn")
            pw_btn.setToolTip("Đổi mật khẩu")
            pw_btn.clicked.connect(lambda _, uid=u["id"]: self._change_pw(uid))
            btn_l.addWidget(edit_btn)
            btn_l.addWidget(del_btn)
            btn_l.addWidget(pw_btn)
            self.table.setCellWidget(i, 7, btn_w)
        self.table.setRowHeight(0, 40)
        for r in range(self.table.rowCount()):
            self.table.setRowHeight(r, 40)

    def _add_user(self):
        dlg = UserDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                user_model.create_user(**d)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _edit_user(self, uid):
        users = user_model.get_all_users()
        u = next((x for x in users if x["id"] == uid), None)
        if not u:
            return
        dlg = UserDialog(self, u)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                user_model.update_user(uid, d["full_name"], d["phone"], d["email"],
                                       d["role_id"], d["hotel_id"], 1)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _delete_user(self, uid):
        if uid == self.current_user["id"]:
            QMessageBox.warning(self, "Cảnh báo", "Không thể vô hiệu hóa chính mình!")
            return
        r = QMessageBox.question(self, "Xác nhận", "Vô hiệu hóa tài khoản này?")
        if r == QMessageBox.StandardButton.Yes:
            user_model.delete_user(uid)
            self.refresh()

    def _change_pw(self, uid):
        from PyQt6.QtWidgets import QInputDialog
        pw, ok = QInputDialog.getText(self, "Đổi mật khẩu", "Mật khẩu mới:",
                                       QLineEdit.EchoMode.Password)
        if ok and pw:
            user_model.change_password(uid, pw)
            QMessageBox.information(self, "Thành công", "Đã đổi mật khẩu.")



