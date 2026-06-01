from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt


def make_table(columns: list[str]) -> QTableWidget:
    t = QTableWidget()
    t.setColumnCount(len(columns))
    t.setHorizontalHeaderLabels(columns)
    hv = t.horizontalHeader()
    hv.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    hv.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    hv.setSectionResizeMode(len(columns) - 1, QHeaderView.ResizeMode.ResizeToContents)
    t.setAlternatingRowColors(True)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    return t


def cell(text: str, color: str | None = None) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    if color:
        item.setForeground(QColor(color))
    return item
