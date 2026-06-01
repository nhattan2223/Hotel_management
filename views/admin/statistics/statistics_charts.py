import datetime
import calendar

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models import invoice_model


def draw_revenue(tab, hotel_id, year, month):
    tab.rev_fig.clear()
    ax = tab.rev_fig.add_subplot(111)
    ax.set_facecolor("white")

    ids = _get_hotel_ids(tab, hotel_id)
    total_rev = 0

    if month:
        data = {}
        for hid in ids:
            rows = invoice_model.get_revenue_by_day(hid, year, month)
            for r in rows:
                d = int(r["day"])
                data[d] = data.get(d, 0) + r["total"]
        days_in_month = calendar.monthrange(year, month)[1]
        xs = list(range(1, days_in_month + 1))
        ys = [data.get(d, 0) / 1_000_000 for d in xs]
        total_rev = sum(data.values())
        ax.bar(xs, ys, color="#3B82F6", alpha=0.9, width=0.7, zorder=3)
        ax.set_xlabel("Ngày", fontsize=9)
        title_str = f"Doanh thu Tháng {month}/{year}"
    else:
        data = {}
        for hid in ids:
            rows = invoice_model.get_revenue_by_month(hid, year)
            for r in rows:
                m = int(r["month"])
                data[m] = data.get(m, 0) + r["total"]
        xs = list(range(1, 13))
        ys = [data.get(m, 0) / 1_000_000 for m in xs]
        total_rev = sum(data.values())
        ax.bar(xs, ys, color="#3B82F6", alpha=0.9, width=0.7, zorder=3)
        ax.set_xticks(xs)
        ax.set_xticklabels([f"T{m}" for m in xs], fontsize=8)
        title_str = f"Doanh thu Năm {year}"

    ax.set_ylabel("Triệu đồng", fontsize=9)
    ax.set_title(title_str, fontsize=11, color="#1E293B", pad=10)
    ax.grid(axis="y", alpha=0.18, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    tab.rev_fig.tight_layout()
    tab.rev_canvas.draw()

    while tab.cards_layout.count():
        tab.cards_layout.takeAt(0).widget().deleteLater()
    _make_stat_card(tab, "💰 Tổng doanh thu", f"{int(total_rev):,} đ")


def draw_occupancy(tab, hotel_id):
    tab.occ_fig.clear()
    ids = _get_hotel_ids(tab, hotel_id)
    total, occ = 0, 0
    for hid in ids:
        s = invoice_model.get_occupancy_stats(hid)
        total += s["total"]
        occ += s["occupied"]

    rate = round(occ / total * 100, 1) if total else 0
    free = total - occ

    ax = tab.occ_fig.add_subplot(111)
    ax.set_facecolor("white")
    if total > 0:
        wedges, texts, autotexts = ax.pie(
            [occ, free],
            labels=["Đang ở", "Trống"],
            autopct="%1.1f%%",
            colors=["#3B82F6", "#E8EEF7"],
            startangle=90,
            wedgeprops={"linewidth": 2, "edgecolor": "white"}
        )
        for t in autotexts:
            t.set_fontsize(9)
            t.set_color("white")
    ax.set_title(f"Lấp đầy: {rate}%\n({occ}/{total} phòng)",
                 fontsize=10, color="#1E293B")
    tab.occ_fig.tight_layout()
    tab.occ_canvas.draw()

    _make_stat_card(tab, "🛏 Tỷ lệ lấp đầy", f"{rate}%")
    _make_stat_card(tab, "🏨 Tổng phòng", f"{total}")
    _make_stat_card(tab, "✅ Đang ở", f"{occ}")


def draw_top(tab, hotel_id):
    ids = _get_hotel_ids(tab, hotel_id)
    combined = {}
    for hid in ids:
        rows = invoice_model.get_top_customers(hid, 20)
        for r in rows:
            k = r["full_name"]
            if k in combined:
                combined[k]["stays"] += r["stays"]
                combined[k]["total_spent"] += (r["total_spent"] or 0)
            else:
                combined[k] = {**r, "total_spent": r["total_spent"] or 0}
    sorted_top = sorted(combined.values(), key=lambda x: x["total_spent"], reverse=True)[:10]

    tab.top_table.setRowCount(len(sorted_top))
    for i, c in enumerate(sorted_top):
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        vals = [c["full_name"], c["phone"] or "—", str(c["stays"]),
                f"{int(c['total_spent']):,} đ"]
        for j, v in enumerate(vals):
            item = QTableWidgetItem(v)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tab.top_table.setItem(i, j, item)


def _get_hotel_ids(tab, hotel_id):
    if hotel_id:
        return [hotel_id]
    return [h["id"] for h in tab.hotels]


def _make_stat_card(tab, label: str, value: str):
    card = QFrame()
    card.setObjectName("StatCard")
    card.setMinimumHeight(80)
    card.setMinimumWidth(180)
    card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    cl = QVBoxLayout(card)
    lbl = QLabel(label)
    lbl.setObjectName("CardTitle")
    val = QLabel(value)
    val.setObjectName("CardValue")
    val.setWordWrap(True)
    cl.addWidget(lbl)
    cl.addWidget(val)
    tab.cards_layout.addWidget(card)
