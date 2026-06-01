"""
PDF invoice generation using ReportLab.
"""
import datetime
import html

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from models import invoice_model
from services.booking_service import compute_invoice
from services.invoice_fonts import register_fonts
from services.invoice_styles import DARK, GRID, TEAL, styles
from services.invoice_tables import info_table, section, summary_table, total_table
from utils.config import BOOKING_CHECKED_OUT, PAYMENT_STATUS_PAID


def generate_invoice_pdf(
    booking_id: int,
    save_path: str,
    hotel_info: dict,
    payment_method: str | None = None,
    payment_status: str = PAYMENT_STATUS_PAID,
) -> bool:
    data = compute_invoice(booking_id)
    if not data:
        return False

    booking = data["booking"]
    if booking.get("status") != BOOKING_CHECKED_OUT:
        return False

    register_fonts()
    style_map = styles()
    elements = []

    doc = SimpleDocTemplate(
        save_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title=f"Hoa don #{booking_id}",
        author=hotel_info.get("name", "Hotel Management System"),
    )

    hotel_name = hotel_info.get("name") or "KHÁCH SẠN"
    hotel_address = hotel_info.get("address") or ""
    hotel_phone = hotel_info.get("phone") or "-"
    hotel_email = hotel_info.get("email") or "-"

    elements.append(Paragraph(html.escape(hotel_name), style_map["hotel"]))
    if hotel_address:
        elements.append(Paragraph(html.escape(hotel_address), style_map["sub"]))
    elements.append(
        Paragraph(
            f"SĐT: {html.escape(hotel_phone)} | Email: {html.escape(hotel_email)}",
            style_map["sub"],
        )
    )
    elements.append(Spacer(1, 0.25 * cm))
    elements.append(HRFlowable(width="100%", thickness=1.4, color=TEAL))
    elements.append(Spacer(1, 0.28 * cm))

    elements.append(Paragraph("HÓA ĐƠN THANH TOÁN", style_map["title"]))
    elements.append(Paragraph(f"Ngày xuất: {datetime.datetime.now():%d/%m/%Y %H:%M}", style_map["sub"]))
    elements.append(Paragraph(f"Mã booking: #{booking_id}", style_map["sub"]))
    elements.append(Paragraph(
        f"Người thu tiền: {html.escape(booking.get('checked_out_by_name') or '-')}",
        style_map["sub"],
    ))
    elements.append(Spacer(1, 0.35 * cm))

    ci = datetime.datetime.fromisoformat(booking["check_in_date"]).strftime("%d/%m/%Y %H:%M")
    co = datetime.datetime.fromisoformat(booking["check_out_date"]).strftime("%d/%m/%Y %H:%M")
    # Lấy danh sách tất cả phòng trong booking (kể cả phòng phụ)
    room_details = data.get("room_charge_details") or []
    if room_details:
        all_rooms_str = ", ".join(str(d["room_number"]) for d in room_details)
        all_types_str = ", ".join(dict.fromkeys(d["room_type_name"] for d in room_details))
    else:
        all_rooms_str = booking["room_number"]
        all_types_str = booking["type_name"]
    info_rows = [
        ["Khách hàng:", booking["customer_name"], "Phòng:", all_rooms_str],
        ["CCCD/Hộ chiếu:", booking.get("id_card") or "-", "Loại phòng:", all_types_str],
        ["Số điện thoại:", booking.get("customer_phone") or "-", "Số đêm:", str(data["nights"])],
        ["Ngày nhận phòng:", ci, "Ngày trả phòng:", co],
    ]
    elements.append(info_table(info_rows, style_map))
    elements.append(Spacer(1, 0.35 * cm))

    room_rows = []
    if data.get("room_charge_details"):
        for detail in data["room_charge_details"]:
            room_rows.append([
                f"Phòng {detail['room_number']} - {detail['room_type_name']}",
                f"{detail['nights']} đêm",
                detail["price_snapshot"],
                detail["amount"],
            ])
    else:
        room_rows.append([
            f"Phòng {booking['room_number']} - {booking['type_name']}",
            f"{data['nights']} đêm",
            booking["price_snapshot"],
            data["room_amount"],
        ])
    elements.extend(section("1. Tiền phòng", room_rows, data["room_amount"], style_map))

    if data["services"]:
        service_rows = [
            [
                s["service_name"],
                str(s["quantity"]),
                s["unit_price"],
                s["quantity"] * s["unit_price"],
            ]
            for s in data["services"]
        ]
        elements.extend(section("2. Dịch vụ", service_rows, data["service_amount"], style_map))

    if data["meals"]:
        meal_rows = [
            [
                f"{m['item_name']} ({m['meal_type_name']})",
                str(m["quantity"]),
                m["unit_price"],
                m["quantity"] * m["unit_price"],
            ]
            for m in data["meals"]
        ]
        elements.extend(section("3. Ẩm thực (F&B)", meal_rows, data["meal_amount"], style_map))

    elements.append(Spacer(1, 0.35 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=GRID))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(summary_table(data, style_map))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(total_table(data["final_amount"], style_map))
    elements.append(Spacer(1, 0.7 * cm))
    elements.append(Paragraph("Cảm ơn quý khách đã lựa chọn dịch vụ của chúng tôi!", style_map["thanks"]))

    doc.build(elements)

    if payment_method is not None:
        invoice_model.upsert_invoice(
            booking_id,
            data["room_amount"],
            data["service_amount"],
            data["meal_amount"],
            data["tax"],
            data["discount"],
            data["final_amount"],
            payment_method,
            payment_status,
        )
    return True