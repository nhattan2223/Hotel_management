from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit,
    QTabWidget, QSpinBox, QAbstractSpinBox, QPushButton,
    QTableWidget, QHeaderView, QWidget,
)
from PyQt6.QtCore import QDate

from models import menu_model


def build_menu_panel(tab) -> QFrame:
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 12, 12, 12)

    title = QLabel("Chọn món")
    title.setObjectName("SectionHeader")
    layout.addWidget(title)

    date_row = QHBoxLayout()
    date_lbl = QLabel("Ngày order:")
    date_lbl.setStyleSheet("font-size:13px; font-weight:bold;")
    tab.date_display = QLineEdit(QDate.currentDate().toString("dd/MM/yyyy"))
    tab.date_display.setReadOnly(True)
    tab.date_display.setFixedWidth(140)
    tab.date_display.setStyleSheet(
        "QLineEdit { background:#F5F8FA; border:1px solid #CBD5E0; border-radius:6px; padding:6px; }"
    )
    date_row.addWidget(date_lbl)
    date_row.addWidget(tab.date_display)
    date_row.addStretch()
    layout.addLayout(date_row)

    tab.meal_tabs = QTabWidget()
    tab._meal_types = menu_model.get_meal_types()
    tab._item_spinboxes = {}

    seen = set()
    for mt in tab._meal_types:
        if mt["name"] in seen:
            continue
        seen.add(mt["name"])

        tab_w = QWidget()
        tab_l = QVBoxLayout(tab_w)
        tab_l.setSpacing(6)
        items = menu_model.get_menu_items(mt["id"], active_only=True)
        if items:
            for item in items:
                row = QHBoxLayout()
                name_lbl = QLabel(f"{item['item_name']}  –  {int(item['price']):,} đ")
                name_lbl.setMinimumWidth(200)
                qty = QSpinBox()
                qty.setRange(0, 99)
                qty.setFixedWidth(70)
                qty.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
                qty.setStyleSheet("QSpinBox { font-size: 13px; font-weight: bold; }")
                tab._item_spinboxes[item["id"]] = (qty, item["price"])
                row.addWidget(name_lbl)
                row.addStretch()
                row.addWidget(qty)
                tab_l.addLayout(row)
            tab_l.addStretch()
            tab.meal_tabs.addTab(tab_w, mt["name"])

    layout.addWidget(tab.meal_tabs)

    add_btn = QPushButton("✅ Thêm vào đơn")
    add_btn.setObjectName("PrimaryBtn")
    add_btn.clicked.connect(tab._add_to_order)
    layout.addWidget(add_btn)
    return frame


def build_orders_panel(tab) -> QFrame:
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 12, 12, 12)

    title = QLabel("Đơn hiện tại")
    title.setObjectName("SectionHeader")
    layout.addWidget(title)

    tab.orders_table = QTableWidget()
    tab.orders_table.setColumnCount(6)
    tab.orders_table.setHorizontalHeaderLabels(["ID", "Bữa", "Món", "SL", "Giá", "Xóa"])
    hv = tab.orders_table.horizontalHeader()
    hv.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    hv.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
    tab.orders_table.setAlternatingRowColors(True)
    tab.orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    layout.addWidget(tab.orders_table)

    tab.order_total_lbl = QLabel("Tổng: 0 đ")
    tab.order_total_lbl.setStyleSheet("font-size:14px;font-weight:bold;color:#00B4A6;")
    layout.addWidget(tab.order_total_lbl)
    return frame
