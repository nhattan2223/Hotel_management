"""
ServiceTab — quản lý dịch vụ cho receptionist.
Dialogs nằm ở service_dialogs.py
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QDialog, QComboBox,
    QMessageBox, QTabWidget,
)
from PyQt6.QtCore import Qt

from models import service_model, booking_model
from utils.config import BOOKING_CHECKED_IN
from views.receptionist.service.service_dialogs import AddServiceOrderDialog, ServiceDialog
from views.receptionist.service.service_helpers import make_table, cell


class ServiceTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.hotel_id = user["hotel_id"]
        self._setup_ui()
        self.refresh()

    # ── Build UI ───────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addLayout(self._build_header())

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_order_tab(), "🛎 Gọi dịch vụ")
        self.tabs.addTab(self._build_mgmt_tab(),  "⚙️ Quản lý dịch vụ")
        layout.addWidget(self.tabs)

        self.booking_combo.currentIndexChanged.connect(self._load_booking_services)

    def _build_header(self) -> QHBoxLayout:
        hdr = QHBoxLayout()
        title = QLabel("🛎 Dịch vụ")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        btn = QPushButton("🔄 Làm mới")
        btn.setObjectName("SecondaryBtn")
        btn.clicked.connect(self.refresh)
        hdr.addWidget(btn)
        return hdr

    def _build_order_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        row = QHBoxLayout()
        row.addWidget(QLabel("Phòng đang ở:"))
        self.booking_combo = QComboBox()
        self.booking_combo.setMinimumWidth(320)
        row.addWidget(self.booking_combo)
        row.addStretch()
        add_btn = QPushButton("+ Thêm dịch vụ")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.clicked.connect(self._add_service_order)
        row.addWidget(add_btn)
        layout.addLayout(row)

        self.empty_banner = QLabel(
            "⚠️  Chưa có phòng nào đang check-in. Vui lòng check-in khách trước."
        )
        self.empty_banner.setStyleSheet(
            "background:#FEF3DC;color:#8B6914;border-radius:8px;padding:10px 14px;font-size:13px;"
        )
        self.empty_banner.setWordWrap(True)
        self.empty_banner.setVisible(False)
        layout.addWidget(self.empty_banner)

        self.svc_table = make_table(["ID", "Dịch vụ", "Số lượng", "Đơn giá (đ)", "Thành tiền (đ)", "Xóa"])
        layout.addWidget(self.svc_table)

        self.svc_total_lbl = QLabel("Tổng dịch vụ: 0 đ")
        self.svc_total_lbl.setStyleSheet("font-size:14px;font-weight:bold;color:#00B4A6;padding:4px 0;")
        layout.addWidget(self.svc_total_lbl)
        return w

    def _build_mgmt_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Danh sách dịch vụ của khách sạn"))
        hdr.addStretch()
        add_btn = QPushButton("+ Thêm dịch vụ mới")
        add_btn.setObjectName("SecondaryBtn")
        add_btn.clicked.connect(self._add_service)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.mgmt_table = make_table(["ID", "Tên dịch vụ", "Giá (đ)", "Tồn kho", "Kích hoạt", "Thao tác"])
        layout.addWidget(self.mgmt_table)
        return w

    # ── Data ───────────────────────────────────────────────────────────────────

    def refresh(self):
        self.booking_combo.blockSignals(True)
        self.booking_combo.clear()
        bookings = booking_model.get_bookings(self.hotel_id, BOOKING_CHECKED_IN)
        for b in bookings:
            self.booking_combo.addItem(
                f"#{b['id']}  Phòng {b['room_number']}  –  {b['customer_name']}", b["id"]
            )
        self.booking_combo.blockSignals(False)
        self.empty_banner.setVisible(len(bookings) == 0)
        self._load_booking_services()
        self._load_services()

    def _load_booking_services(self):
        bid = self.booking_combo.currentData()
        if bid is None:
            self.svc_table.setRowCount(0)
            self.svc_total_lbl.setText("Tổng dịch vụ: 0 đ")
            return

        svcs = service_model.get_booking_services(bid)
        self.svc_table.setRowCount(len(svcs))
        total = 0
        for i, s in enumerate(svcs):
            amt = s["quantity"] * s["unit_price"]
            total += amt
            for j, v in enumerate([
                str(s["id"]), s["service_name"], str(s["quantity"]),
                f"{int(s['unit_price']):,}", f"{int(amt):,}",
            ]):
                self.svc_table.setItem(i, j, cell(v))

            del_btn = QPushButton("🗑")
            del_btn.setObjectName("IconBtn")
            del_btn.setToolTip("Xóa dịch vụ này")
            del_btn.clicked.connect(lambda _, bsid=s["id"]: self._del_booking_service(bsid))
            self.svc_table.setCellWidget(i, 5, del_btn)
            self.svc_table.setRowHeight(i, 40)

        self.svc_total_lbl.setText(f"Tổng dịch vụ: {int(total):,} đ")

    def _load_services(self):
        svcs = service_model.get_services(active_only=False)
        self.mgmt_table.setRowCount(len(svcs))
        for i, s in enumerate(svcs):
            stk_str   = str(s["stocking"]) if s["stocking"] is not None else "Không giới hạn"
            is_active = bool(s["is_active"])
            for j, v in enumerate([
                str(s["id"]), s["service_name"], f"{int(s['price']):,}", stk_str,
                "✅ Có" if is_active else "❌ Tắt",
            ]):
                color = ("#27AE60" if is_active else "#E74C3C") if j == 4 else None
                self.mgmt_table.setItem(i, j, cell(v, color))

            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(4, 2, 4, 2)
            btn_l.setSpacing(6)

            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("IconBtn")
            edit_btn.setToolTip("Chỉnh sửa")
            edit_btn.clicked.connect(lambda _, sid=s["id"]: self._edit_service(sid))

            toggle_btn = QPushButton("🔄")
            toggle_btn.setObjectName("IconBtn")
            toggle_btn.setToolTip("Bật / Tắt")
            toggle_btn.clicked.connect(
                lambda _, sid=s["id"], act=s["is_active"]: self._toggle_service(sid, act)
            )

            btn_l.addWidget(edit_btn)
            btn_l.addWidget(toggle_btn)
            self.mgmt_table.setCellWidget(i, 5, btn_w)
            self.mgmt_table.setRowHeight(i, 40)

    # ── Handlers ───────────────────────────────────────────────────────────────

    def _add_service_order(self):
        bid = self.booking_combo.currentData()
        if bid is None:
            QMessageBox.warning(self, "Lỗi", "Chưa có phòng nào đang check-in.\nVui lòng check-in khách trước.")
            return
        active_svcs = service_model.get_services(active_only=True)
        if not active_svcs:
            QMessageBox.information(self, "Thông báo", "Hiện không có dịch vụ nào đang hoạt động.")
            return
        dlg = AddServiceOrderDialog(active_svcs, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            sid, qty, price = dlg.get_data()
            try:
                service_model.add_booking_service(bid, sid, qty, price)
            except ValueError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
                return
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))
                return
            self._load_booking_services()
            self._load_services()

    def _del_booking_service(self, bsid: int):
        if QMessageBox.question(self, "Xác nhận", "Xóa dịch vụ này khỏi booking?") == QMessageBox.StandardButton.Yes:
            service_model.delete_booking_service(bsid)
            self._load_booking_services()
            self._load_services()

    def _add_service(self):
        dlg = ServiceDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                service_model.create_service(d["stocking"], d["name"], d["price"])
                self._load_services()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _edit_service(self, sid: int):
        s = service_model.get_service(sid)
        if not s:
            return
        dlg = ServiceDialog(service=s, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                service_model.update_service(sid, d["stocking"], d["name"], d["price"], s["is_active"])
                self._load_services()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _toggle_service(self, sid: int, current_active: int):
        s = service_model.get_service(sid)
        if s:
            service_model.update_service(
                sid, s["stocking"], s["service_name"], s["price"],
                0 if current_active else 1,
            )
            self._load_services()
