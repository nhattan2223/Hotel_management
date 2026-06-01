import datetime

from PyQt6.QtWidgets import QWidget, QToolTip
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QPen,
    QBrush,
    QPainterPath,
)

from utils.config import BOOKING_STATUS_VN, BOOKING_RESERVED, BOOKING_CHECKED_IN, BOOKING_CHECKED_OUT


# Colors for booking status bars
BAR_COLORS = {
    BOOKING_RESERVED:    ("#F39C12", "#FFF3DC"),
    BOOKING_CHECKED_IN:  ("#00B4A6", "#E0F7F5"),
    BOOKING_CHECKED_OUT: ("#95A5A6", "#F0F0F0"),
}

ROW_H   = 44
HDR_H   = 56
LABE_W  = 110
DAY_W   = 38
PAD     = 4


class GanttCanvas(QWidget):
    booking_clicked = pyqtSignal(int, int)  # emit booking id, room id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rooms: list[dict] = []        # [{id, room_number, type_name, floor}]
        self._bookings: list[dict] = []     # from get_all_bookings_for_gantt
        self._start_date = datetime.date.today()
        self._days = 30
        self.setMouseTracking(True)
        self._hover_bid = None

    def set_data(self, rooms, bookings, start_date, days=30):
        self._rooms = rooms
        self._bookings = bookings
        self._start_date = start_date
        self._days = days
        w = LABE_W + days * DAY_W + 20
        h = HDR_H + len(rooms) * ROW_H + 10
        self.setMinimumSize(w, h)
        self.update()

    def paintEvent(self, event):
        if not self._rooms:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw(p)
        p.end()

    def _draw(self, p: QPainter):
        W = self.width()
        H = self.height()

        # Background
        p.fillRect(0, 0, W, H, QColor("#F0FAFA"))

        # ── Header row (dates) ─────────────────────────────
        p.fillRect(0, 0, W, HDR_H, QColor("#00B4A6"))

        # Room label header
        p.setPen(QPen(QColor("white")))
        f = QFont()
        f.setBold(True)
        f.setPointSize(10)
        p.setFont(f)
        p.drawText(QRect(0, 0, LABE_W, HDR_H), Qt.AlignmentFlag.AlignCenter, "Phòng")

        today = datetime.date.today()

        f2 = QFont(); f2.setPointSize(9); f2.setBold(True)
        f3 = QFont(); f3.setPointSize(8)
        for i in range(self._days):
            d = self._start_date + datetime.timedelta(days=i)
            x = LABE_W + i * DAY_W
            # Highlight today
            if d == today:
                p.fillRect(x, 0, DAY_W, HDR_H, QColor("#008F83"))

            p.setFont(f3)
            p.setPen(QPen(QColor("rgba(255,255,255,180)")))
            day_names = ["T2","T3","T4","T5","T6","T7","CN"]
            p.drawText(QRect(x, 4, DAY_W, 16), Qt.AlignmentFlag.AlignCenter,
                       day_names[d.weekday()])
            p.setFont(f2)
            p.setPen(QPen(QColor("white")))
            p.drawText(QRect(x, 20, DAY_W, 22), Qt.AlignmentFlag.AlignCenter,
                       str(d.day))
            # Month change marker
            if d.day == 1:
                p.setPen(QPen(QColor("rgba(255,255,255,120)")))
                p.setFont(QFont())
                f_s = QFont(); f_s.setPointSize(7)
                p.setFont(f_s)
                p.drawText(QRect(x, 40, DAY_W*2, 14), Qt.AlignmentFlag.AlignLeft,
                           f"T{d.month}")

        # ── Room rows ──────────────────────────────────────
        for ri, room in enumerate(self._rooms):
            y = HDR_H + ri * ROW_H
            bg = QColor("white") if ri % 2 == 0 else QColor("#F5FFFE")
            p.fillRect(0, y, W, ROW_H, bg)

            # Room label
            p.fillRect(0, y, LABE_W, ROW_H, QColor("#E0F7F5"))
            f_room = QFont(); f_room.setBold(True); f_room.setPointSize(10)
            p.setFont(f_room)
            p.setPen(QPen(QColor("#00B4A6")))
            p.drawText(QRect(4, y, LABE_W - 8, ROW_H//2 + 2),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                       f"  {room['room_number']}")
            f_type = QFont(); f_type.setPointSize(8)
            p.setFont(f_type)
            p.setPen(QPen(QColor("#4A6572")))
            p.drawText(QRect(4, y + ROW_H//2, LABE_W - 8, ROW_H//2),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                       f"  {room['type_name']}")

            # Today vertical highlight
            if 0 <= (today - self._start_date).days < self._days:
                today_x = LABE_W + (today - self._start_date).days * DAY_W
                p.fillRect(today_x, y, DAY_W, ROW_H, QColor("rgba(0,180,166,20)"))

        # ── Vertical grid lines ───────────────────────────
        p.setPen(QPen(QColor("#D4ECEB"), 0.5))
        for i in range(self._days + 1):
            x = LABE_W + i * DAY_W
            p.drawLine(x, HDR_H, x, HDR_H + len(self._rooms) * ROW_H)

        # Horizontal grid lines
        for ri in range(len(self._rooms) + 1):
            y = HDR_H + ri * ROW_H
            p.drawLine(0, y, W, y)

        # ── Booking bars ──────────────────────────────────
        room_index = {r["id"]: i for i, r in enumerate(self._rooms)}
        for bk in self._bookings:
            if bk["room_id"] not in room_index:
                continue
            ri = room_index[bk["room_id"]]
            y = HDR_H + ri * ROW_H

            ci = datetime.datetime.fromisoformat(bk["check_in_date"]).date()
            co = datetime.datetime.fromisoformat(bk["check_out_date"]).date()

            # Clamp to visible range
            bar_start = max(ci, self._start_date)
            bar_end   = min(co, self._start_date + datetime.timedelta(days=self._days))
            if bar_start >= bar_end:
                continue

            x1 = LABE_W + (bar_start - self._start_date).days * DAY_W
            x2 = LABE_W + (bar_end   - self._start_date).days * DAY_W

            status = bk.get("status", BOOKING_RESERVED)
            bar_color, _ = BAR_COLORS.get(status, ("#00B4A6", "#E0F7F5"))

            is_hover = (self._hover_bid == bk["id"])
            color = QColor(bar_color)
            if is_hover:
                color = color.lighter(115)

            path = QPainterPath()
            r = QRect(x1 + PAD, y + PAD, x2 - x1 - PAD*2, ROW_H - PAD*2)
            path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), 6, 6)
            p.fillPath(path, QBrush(color))

            # Text on bar
            p.setPen(QPen(QColor("white")))
            f_bar = QFont(); f_bar.setPointSize(9); f_bar.setBold(True)
            p.setFont(f_bar)
            name = bk.get("customer_name", "")
            p.drawText(r.adjusted(6, 0, -4, 0),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                       name[:16] + ("…" if len(name) > 16 else ""))

        # Left border separator
        p.setPen(QPen(QColor("#B2DFDB"), 1.5))
        p.drawLine(LABE_W, 0, LABE_W, H)

    def mouseMoveEvent(self, event):
        bk = self._booking_at(event.pos())
        bid = bk["id"] if bk is not None else None
        if bid != self._hover_bid:
            self._hover_bid = bid
            self.update()
        if bk is not None:
            ci = datetime.datetime.fromisoformat(bk["check_in_date"]).strftime("%d/%m/%Y")
            co = datetime.datetime.fromisoformat(bk["check_out_date"]).strftime("%d/%m/%Y")
            status_vn = BOOKING_STATUS_VN.get(bk['status'], bk['status'])
            QToolTip.showText(
                event.globalPosition().toPoint(),
                f"#{bk['id']} {bk['customer_name']}\n"
                f"{ci} → {co}\n"
                f"Trạng thái: {status_vn}"
            )
        else:
            QToolTip.hideText()

    def mousePressEvent(self, event):
        bk = self._booking_at(event.pos())
        if bk is not None:
            self.booking_clicked.emit(bk["id"], bk["room_id"])

    def _booking_at(self, pos: QPoint) -> dict | None:
        room_index = {r["id"]: i for i, r in enumerate(self._rooms)}
        for bk in self._bookings:
            if bk["room_id"] not in room_index:
                continue
            ri = room_index[bk["room_id"]]
            y = HDR_H + ri * ROW_H
            ci = datetime.datetime.fromisoformat(bk["check_in_date"]).date()
            co = datetime.datetime.fromisoformat(bk["check_out_date"]).date()
            bar_start = max(ci, self._start_date)
            bar_end   = min(co, self._start_date + datetime.timedelta(days=self._days))
            if bar_start >= bar_end:
                continue
            x1 = LABE_W + (bar_start - self._start_date).days * DAY_W
            x2 = LABE_W + (bar_end - self._start_date).days * DAY_W
            r = QRect(x1 + PAD, y + PAD, x2 - x1 - PAD*2, ROW_H - PAD*2)
            if r.contains(pos):
                return bk
        return None

