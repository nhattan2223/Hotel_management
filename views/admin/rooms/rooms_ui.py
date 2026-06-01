from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWidgets import QHeaderView

from models import hotel_model


def setup_rooms_ui(tab: QWidget) -> None:
    """
    Build all widgets/layouts for AdminRoomsTab.

    This function only constructs UI and wires top-level signals.
    Data binding is handled by tab.refresh and presenter helpers.
    """
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(16)

    hdr = QHBoxLayout()
    title = QLabel("🛏 Danh sách Phòng")
    title.setObjectName("PageTitle")
    hdr.addWidget(title)
    hdr.addStretch()

    hdr.addWidget(QLabel("Chi nhánh:"))
    tab.hotel_combo = QComboBox()
    tab.hotels = hotel_model.get_all_hotels()
    tab.hotel_combo.addItem("Tất cả", None)
    for h in tab.hotels:
        tab.hotel_combo.addItem(h["name"], h["id"])
    tab.hotel_combo.currentIndexChanged.connect(tab.refresh)
    hdr.addWidget(tab.hotel_combo)

    add_room_btn = QPushButton("+ Thêm phòng")
    add_room_btn.setObjectName("PrimaryBtn")
    add_room_btn.clicked.connect(tab._add_room)
    hdr.addWidget(add_room_btn)

    add_type_btn = QPushButton("+ Loại phòng")
    add_type_btn.setObjectName("SecondaryBtn")
    add_type_btn.clicked.connect(tab._manage_types)
    hdr.addWidget(add_type_btn)

    layout.addLayout(hdr)

    tabs = QTabWidget()

    # Rooms tab
    rooms_w = QWidget()
    rooms_l = QVBoxLayout(rooms_w)
    rooms_l.setContentsMargins(0, 12, 0, 0)
    tab.table = QTableWidget()
    tab.table.setColumnCount(8)
    tab.table.setHorizontalHeaderLabels(
        ["ID", "Chi nhánh", "Phòng", "Tầng", "Loại phòng", "Giá/đêm", "Trạng thái", "Thao tác"]
    )
    tab.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    tab.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    tab.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
    tab.table.setAlternatingRowColors(True)
    tab.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    rooms_l.addWidget(tab.table)
    tabs.addTab(rooms_w, "Phòng")

    # Room types tab
    types_w = QWidget()
    types_l = QVBoxLayout(types_w)
    types_l.setContentsMargins(0, 12, 0, 0)
    tab.types_table = QTableWidget()
    tab.types_table.setColumnCount(5)
    tab.types_table.setHorizontalHeaderLabels(
        ["ID", "Loại phòng", "Giá/đêm", "Tối đa khách", "Thao tác"]
    )
    tab.types_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    tab.types_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
    tab.types_table.setAlternatingRowColors(True)
    tab.types_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    types_l.addWidget(tab.types_table)
    tabs.addTab(types_w, "Loại phòng")

    layout.addWidget(tabs)

