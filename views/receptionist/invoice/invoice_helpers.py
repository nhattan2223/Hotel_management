from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView
from PyQt6.QtCore import Qt


def _bold(text: str, size: int = 13) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-size:{size}px; font-weight:bold; color:#1A2E35;")
    return lbl


def _section_lbl(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "font-size:13px; font-weight:bold; color:#00B4A6;"
        "border-bottom:2px solid #B2DFDB; padding-bottom:4px;"
    )
    return lbl


def _make_table(headers: list) -> QTableWidget:
    t = QTableWidget()
    t.setColumnCount(len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.setAlternatingRowColors(True)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    # Set min/max height to prevent tables from overlapping
    t.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Preferred
    )
    t.setMinimumHeight(60)
    t.setMaximumHeight(200)
    return t


def _fill_row(table: QTableWidget, row: int, values: list):
    for j, v in enumerate(values):
        item = QTableWidgetItem(v)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, j, item)
    table.setRowHeight(row, 36)


def _adjust_table_height(table: QTableWidget):
    rows = table.rowCount()
    header_height = table.horizontalHeader().height() or 30
    row_height = table.rowHeight(0) if rows > 0 else 36
    table.setFixedHeight(header_height + rows * row_height + 12)

