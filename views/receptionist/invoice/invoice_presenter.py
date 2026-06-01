import datetime

from utils.config import BOOKING_STATUS_COLOR, BOOKING_STATUS_VN
from views.receptionist.invoice.invoice_helpers import _adjust_table_height, _fill_row


def clear_preview(tab) -> None:
    tab._current_data = None
    for lbl in [
        tab.lbl_customer,
        tab.lbl_idcard,
        tab.lbl_phone,
        tab.lbl_room,
        tab.lbl_type,
        tab.lbl_checkin,
        tab.lbl_checkout,
        tab.lbl_nights,
        tab.lbl_status,
        tab.lbl_cashier,
    ]:
        lbl.setText("—")
    for tbl in [tab.room_table, tab.svc_table, tab.meal_table]:
        tbl.setRowCount(0)
    for lbl in [tab.s_room, tab.s_svc, tab.s_meal, tab.s_tax, tab.s_disc, tab.s_total]:
        lbl.setText("0 đ")

    tab.pdf_btn.setEnabled(False)
    tab.payment_combo.setEnabled(False)
    tab.pdf_btn.setToolTip("Chỉ được xuất hóa đơn sau khi phòng đã check-out.")


def populate_preview(tab, data: dict, invoice_export_status: str) -> None:
    tab._current_data = data
    bk = data["booking"]

    # ── Guest info ─────────────────────────────────────
    ci_str = datetime.datetime.fromisoformat(bk["check_in_date"]).strftime("%d/%m/%Y %H:%M")
    co_str = datetime.datetime.fromisoformat(bk["check_out_date"]).strftime("%d/%m/%Y %H:%M")
    status = bk.get("status", "")

    tab.lbl_customer.setText(bk["customer_name"])
    tab.lbl_idcard.setText(bk.get("id_card") or "—")
    tab.lbl_phone.setText(bk.get("customer_phone") or "—")
    # Hiển thị tất cả phòng trong booking (kể cả phòng phụ)
    room_details = data.get("room_charge_details") or []
    if room_details:
        all_rooms = ", ".join(str(d["room_number"]) for d in room_details)
        all_types = ", ".join(dict.fromkeys(d["room_type_name"] for d in room_details))
    else:
        all_rooms = bk["room_number"]
        all_types = bk["type_name"]
    tab.lbl_room.setText(all_rooms)
    tab.lbl_type.setText(all_types)
    tab.lbl_checkin.setText(ci_str)
    tab.lbl_checkout.setText(co_str)
    tab.lbl_nights.setText(f"{data['nights']} đêm")
    tab.lbl_status.setText(BOOKING_STATUS_VN.get(status, status))
    tab.lbl_status.setStyleSheet(
        f"font-size:13px; font-weight:bold; color:{BOOKING_STATUS_COLOR.get(status,'#1A2E35')};"
    )
    tab.lbl_cashier.setText(bk.get("checked_out_by_name") or "—")

    can_export = status == invoice_export_status
    tab.pdf_btn.setEnabled(can_export)
    tab.payment_combo.setEnabled(can_export)
    tab.pdf_btn.setToolTip("" if can_export else "Chỉ được xuất hóa đơn sau khi phòng đã check-out.")

    # ── Room table ─────────────────────────────────────
    room_details = data.get("room_charge_details") or []
    if room_details:
        tab.room_table.setRowCount(len(room_details))
        for i, detail in enumerate(room_details):
            _fill_row(
                tab.room_table,
                i,
                [
                    f"Phòng {detail['room_number']}",
                    detail['room_type_name'],
                    str(detail['nights']),
                    f"{int(detail['price_snapshot']):,}",
                    f"{int(detail['amount']):,}",
                ],
            )
    else:
        tab.room_table.setRowCount(1)
        _fill_row(
            tab.room_table,
            0,
            [
                f"Phòng {bk['room_number']}",
                bk["type_name"],
                str(data["nights"]),
                f"{int(bk['price_per_night']):,}",
                f"{int(data['room_amount']):,}",
            ],
        )
    _adjust_table_height(tab.room_table)

    # ── Services table ─────────────────────────────────
    svcs = data["services"]
    tab.svc_table.setRowCount(max(len(svcs), 1))
    if svcs:
        for i, s in enumerate(svcs):
            _fill_row(
                tab.svc_table,
                i,
                [
                    s["service_name"],
                    str(s["quantity"]),
                    f"{int(s['unit_price']):,}",
                    f"{int(s['quantity'] * s['unit_price']):,}",
                ],
            )
    else:
        _fill_row(tab.svc_table, 0, ["(Không có dịch vụ)", "—", "—", "—"])
    _adjust_table_height(tab.svc_table)

    # ── Meals table ────────────────────────────────────
    meals = data["meals"]
    tab.meal_table.setRowCount(max(len(meals), 1))
    if meals:
        for i, m in enumerate(meals):
            _fill_row(
                tab.meal_table,
                i,
                [
                    m["item_name"],
                    m["meal_type_name"],
                    str(m["quantity"]),
                    f"{int(m['unit_price']):,}",
                    f"{int(m['quantity'] * m['unit_price']):,}",
                ],
            )
    else:
        _fill_row(tab.meal_table, 0, ["(Không có đặt ăn)", "—", "—", "—", "—"])
    _adjust_table_height(tab.meal_table)

    # ── Summary ────────────────────────────────────────
    tab.s_room.setText(f"{int(data['room_amount']):,} đ")
    tab.s_svc.setText(f"{int(data['service_amount']):,} đ")
    tab.s_meal.setText(f"{int(data['meal_amount']):,} đ")
    tab.s_tax.setText(f"{int(data['tax']):,} đ")
    tab.s_disc.setText(f"- {int(data['discount']):,} đ")
    tab.s_total.setText(f"{int(data['final_amount']):,} đ")