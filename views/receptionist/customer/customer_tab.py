from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QLineEdit, QDialog, QMessageBox,
                              QHeaderView, QFrame)
from PyQt6.QtCore import Qt
import datetime
from models import customer_model
from utils.config import BOOKING_STATUS_VN
from views.receptionist.customer.customer_dialog import CustomerDialog


class CustomerTab(QWidget):
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
        title = QLabel("👤 Khách hàng")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        add_btn = QPushButton("+ Thêm khách hàng")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.clicked.connect(self._add)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        # CCCD lookup
        lookup_frame = QFrame()
        lookup_frame.setObjectName("Card")
        lookup_l = QVBoxLayout(lookup_frame)
        lookup_l.setContentsMargins(16, 16, 16, 16)

        lu_hdr = QLabel("🔍 Tra cứu khách theo CCCD")
        lu_hdr.setObjectName("SectionHeader")
        lookup_l.addWidget(lu_hdr)

        lu_row = QHBoxLayout()
        self.lookup_input = QLineEdit()
        self.lookup_input.setPlaceholderText("Nhập số CCCD / hộ chiếu...")
        self.lookup_input.returnPressed.connect(self._lookup)
        lu_row.addWidget(self.lookup_input)
        lu_btn = QPushButton("Tra cứu")
        lu_btn.setObjectName("PrimaryBtn")
        lu_btn.clicked.connect(self._lookup)
        lu_row.addWidget(lu_btn)
        lookup_l.addLayout(lu_row)

        self.lookup_result = QLabel("")
        self.lookup_result.setWordWrap(True)
        self.lookup_result.setStyleSheet("font-size: 13px; color: #1A2E35; padding: 6px;")
        lookup_l.addWidget(self.lookup_result)

        # Booking history table (hidden until lookup)
        self.booking_history_table = QTableWidget()
        self.booking_history_table.setColumnCount(6)
        self.booking_history_table.setHorizontalHeaderLabels(
            ["Mã booking", "Phòng", "Khách sạn", "Nhận phòng", "Trả phòng", "Trạng thái"]
        )
        self.booking_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.booking_history_table.setAlternatingRowColors(True)
        self.booking_history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.booking_history_table.setVisible(False)
        lookup_l.addWidget(self.booking_history_table)
        layout.addWidget(lookup_frame)

        # Search bar
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm theo tên, CCCD, SĐT...")
        self.search_input.textChanged.connect(self._search)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Họ tên", "CCCD", "Điện thoại", "Email", "Địa chỉ", "Thao tác"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        self._fill_table(customer_model.get_all_customers())

    def _search(self, text):
        if len(text) >= 2:
            self._fill_table(customer_model.search_customers(text))
        else:
            self.refresh()

    def _fill_table(self, customers):
        self.table.setRowCount(len(customers))
        for i, c in enumerate(customers):
            vals = [str(c["id"]), c["full_name"], c["id_card"] or "—",
                    c["phone"] or "—", c["email"] or "—", c["address"] or "—"]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(4, 2, 4, 2)
            btn_l.setSpacing(4)
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("IconBtn")
            edit_btn.clicked.connect(lambda _, cid=c["id"]: self._edit(cid))
            del_btn = QPushButton("🗑")
            del_btn.setObjectName("IconBtn")
            del_btn.clicked.connect(lambda _, cid=c["id"]: self._delete(cid))
            btn_l.addWidget(edit_btn)
            btn_l.addWidget(del_btn)
            self.table.setCellWidget(i, 6, btn_w)
            self.table.setRowHeight(i, 40)

    def _lookup(self):
        id_card = self.lookup_input.text().strip()
        if not id_card:
            return
        cust = customer_model.find_by_id_card(id_card)
        if not cust:
            self.lookup_result.setText(
                f"❌  Không tìm thấy khách với CCCD: {id_card}"
            )
            self.lookup_result.setStyleSheet(
                "font-size: 13px; color: #E74C3C; padding: 6px;"
                "background: #FDE8E6; border-radius: 8px;"
            )
            self.booking_history_table.setVisible(False)
            return

        self.lookup_result.setText(
            f"✅  <b>{cust['full_name']}</b> – CCCD: {cust['id_card']} – SĐT: {cust['phone'] or '—'}"
        )
        self.lookup_result.setStyleSheet(
            "font-size: 13px; color: #27AE60; padding: 6px;"
            "background: #E8FAF0; border-radius: 8px;"
        )

        bookings = customer_model.get_booking_history_by_id_card(id_card)
        if not bookings:
            self.booking_history_table.setVisible(False)
            return

        self.booking_history_table.setRowCount(len(bookings))
        for i, b in enumerate(bookings):
            ci = datetime.datetime.fromisoformat(b["check_in_date"]).strftime("%d/%m/%Y")
            co = datetime.datetime.fromisoformat(b["check_out_date"]).strftime("%d/%m/%Y")
            vals = [
                str(b["id"]),
                b["room_number"],
                b["hotel_name"],
                ci,
                co,
                BOOKING_STATUS_VN.get(b["status"], b["status"])
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.booking_history_table.setItem(i, j, item)
            self.booking_history_table.setRowHeight(i, 32)
        self.booking_history_table.setVisible(True)

    def _add(self):
        dlg = CustomerDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                customer_model.create_customer(**d)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _edit(self, cid):
        c = customer_model.get_customer(cid)
        if not c:
            return
        dlg = CustomerDialog(self, c)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                customer_model.update_customer(cid, **d)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _delete(self, cid):
        r = QMessageBox.question(self, "Xác nhận", "Xóa khách hàng này?")
        if r == QMessageBox.StandardButton.Yes:
            try:
                customer_model.delete_customer(cid)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa: {e}")



