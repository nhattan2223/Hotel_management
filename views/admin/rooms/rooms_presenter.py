from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QTableWidgetItem, QWidget

from utils.config import BOOKING_STATUS_VN, STATUS_DIRTY, STATUS_OCCUPIED


def populate_rooms_table(tab, rooms: list[dict]) -> None:
    tab.table.setRowCount(len(rooms))
    for i, r in enumerate(rooms):
        status_display = r["occupancy_status"]
        if r.get("housekeeping") == STATUS_DIRTY:
            status_display = STATUS_DIRTY

        vals = [
            str(r["id"]),
            r["hotel_name"],
            r["room_number"],
            str(r["floor"] or "—"),
            r["type_name"],
            f"{int(r['price_per_night']):,} đ",
            BOOKING_STATUS_VN.get(status_display, status_display),
        ]
        for j, v in enumerate(vals):
            item = QTableWidgetItem(v)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tab.table.setItem(i, j, item)

        btn_w = QWidget()
        btn_l = QHBoxLayout(btn_w)
        btn_l.setContentsMargins(4, 2, 4, 2)
        edit_btn = QPushButton("✏️")
        edit_btn.setObjectName("IconBtn")
        edit_btn.clicked.connect(lambda _, rid=r["id"]: tab._edit_room(rid))
        del_btn = QPushButton("🗑")
        del_btn.setObjectName("IconBtn")
        del_btn.clicked.connect(lambda _, rid=r["id"]: tab._delete_room(rid))
        btn_l.addWidget(edit_btn)
        btn_l.addWidget(del_btn)
        tab.table.setCellWidget(i, 7, btn_w)
        tab.table.setRowHeight(i, 40)


def populate_room_types_table(tab, types: list[dict]) -> None:
    tab.types_table.setRowCount(len(types))
    for i, t in enumerate(types):
        vals = [
            str(t["id"]),
            t["type_name"],
            f"{int(t['price_per_night']):,} đ",
            str(t["max_guest"]),
        ]
        for j, v in enumerate(vals):
            item = QTableWidgetItem(v)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tab.types_table.setItem(i, j, item)

        btn_w = QWidget()
        btn_l = QHBoxLayout(btn_w)
        btn_l.setContentsMargins(4, 2, 4, 2)
        edit_btn = QPushButton("✏️")
        edit_btn.setObjectName("IconBtn")
        edit_btn.clicked.connect(lambda _, tid=t["id"]: tab._edit_type(tid))
        btn_l.addWidget(edit_btn)
        tab.types_table.setCellWidget(i, 4, btn_w)
        tab.types_table.setRowHeight(i, 40)

