"""
OrderTab — Chef nhận order món ăn cho phòng đang check-in.
Tách ra từ chef_window.py
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from models import menu_model
from views.chef.order.order_panels import build_menu_panel, build_orders_panel


class OrderTab(QWidget):
    """Chef nhận order món ăn trực tiếp cho phòng đang ở."""

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user     = user
        self.hotel_id = user["hotel_id"]
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("🍽 Đặt thực đơn")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("Phòng (đang ở):"))
        self.booking_combo = QComboBox()
        self.booking_combo.setMinimumWidth(300)
        self.booking_combo.currentIndexChanged.connect(self._load_orders)
        sel_row.addWidget(self.booking_combo)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        split = QHBoxLayout()
        split.addWidget(build_menu_panel(self), 2)
        split.addWidget(build_orders_panel(self), 3)
        layout.addLayout(split)

    # ── Data ───────────────────────────────────────────────────────────────────

    def refresh(self):
        bookings = menu_model.get_active_bookings_for_hotel(self.hotel_id)
        self.booking_combo.clear()
        for b in bookings:
            self.booking_combo.addItem(
                f"Phòng {b['room_number']} – {b['customer_name']}", b["id"]
            )
        self._load_orders()

    def _load_orders(self):
        bid = self.booking_combo.currentData()
        if not bid:
            self.orders_table.setRowCount(0)
            return
        meals = menu_model.get_booking_meals(bid)
        self.orders_table.setRowCount(len(meals))
        total = 0
        for i, m in enumerate(meals):
            amt = m["quantity"] * m["unit_price"]
            total += amt
            for j, v in enumerate([
                str(m["id"]), m["meal_type_name"], m["item_name"],
                str(m["quantity"]), f"{int(m['unit_price']):,} đ",
            ]):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.orders_table.setItem(i, j, item)
            del_btn = QPushButton("🗑")
            del_btn.setObjectName("IconBtn")
            del_btn.clicked.connect(lambda _, mid=m["id"]: self._del_meal(mid))
            self.orders_table.setCellWidget(i, 5, del_btn)
            self.orders_table.setRowHeight(i, 36)
        self.order_total_lbl.setText(f"Tổng: {int(total):,} đ")

    # ── Actions ────────────────────────────────────────────────────────────────

    def _add_to_order(self):
        bid = self.booking_combo.currentData()
        if not bid:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn phòng.")
            return
        added = 0
        for item_id, (spin, price) in self._item_spinboxes.items():
            qty = spin.value()
            if qty > 0:
                menu_model.add_booking_meal(bid, item_id, qty, price)
                spin.setValue(0)
                added += 1
        if added:
            self._load_orders()
        else:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn ít nhất 1 món.")

    def _del_meal(self, mid):
        r = QMessageBox.question(self, "Xác nhận", "Xóa món này khỏi đơn?")
        if r == QMessageBox.StandardButton.Yes:
            menu_model.delete_booking_meal(mid)
            self._load_orders()
