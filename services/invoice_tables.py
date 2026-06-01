import html

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Table, TableStyle

from services.invoice_styles import DARK, GRID, LIGHT_TEAL, TEAL


def info_table(rows: list[list[str]], style_map: dict) -> Table:
    table_data = []
    for row in rows:
        table_data.append([
            Paragraph(_esc(row[0]), style_map["cell_bold"]),
            Paragraph(_esc(row[1]), style_map["cell"]),
            Paragraph(_esc(row[2]), style_map["cell_bold"]),
            Paragraph(_esc(row[3]), style_map["cell"]),
        ])

    table = Table(table_data, colWidths=[3.2 * cm, 5.3 * cm, 3.2 * cm, 5.3 * cm])
    table.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_TEAL, colors.white]),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, GRID),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, GRID),
    ]))
    return table


def section(title: str, rows: list[list], subtotal: float, style_map: dict) -> list:
    elements = [Paragraph(_esc(title), style_map["section"])]
    table_data = [[
        Paragraph("Mô tả", style_map["header"]),
        Paragraph("Số lượng", style_map["header"]),
        Paragraph("Đơn giá", style_map["header"]),
        Paragraph("Thành tiền", style_map["header"]),
    ]]

    for row in rows:
        table_data.append([
            Paragraph(_esc(row[0]), style_map["cell"]),
            Paragraph(_esc(row[1]), style_map["cell"]),
            Paragraph(_esc(_money(row[2])), style_map["cell_right"]),
            Paragraph(_esc(_money(row[3])), style_map["cell_right"]),
        ])

    table_data.append([
        "",
        "",
        Paragraph("Tổng:", style_map["cell_bold"]),
        Paragraph(_esc(_money(subtotal)), style_map["cell_right"]),
    ])

    table = Table(table_data, colWidths=[7.5 * cm, 2.5 * cm, 3.5 * cm, 3.5 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("BACKGROUND", (0, -1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, LIGHT_TEAL]),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("SPAN", (0, -1), (1, -1)),
        ("BOX", (0, 0), (-1, -1), 1.5, colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    return elements


def summary_table(data: dict, style_map: dict) -> Table:
    rows = [
        ["Tạm tính:", _money(data["subtotal"])],
        ["Thuế VAT (8%):", _money(data["tax"])],
        ["Đặt cọc / Giảm giá:", f"- {_money(data['discount'])}"],
    ]
    table_data = [
        [Paragraph(_esc(label), style_map["cell"]), Paragraph(_esc(value), style_map["cell_right"])]
        for label, value in rows
    ]
    table = Table(table_data, colWidths=[11 * cm, 6 * cm])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def total_table(final_amount: float, style_map: dict) -> Table:
    total_style = ParagraphStyle(
        "InvoiceTotal",
        parent=style_map["cell_bold"],
        fontSize=12,
        leading=15,
        textColor=colors.white,
    )
    total_right_style = ParagraphStyle(
        "InvoiceTotalRight",
        parent=total_style,
        alignment=style_map["cell_right"].alignment,
    )
    table = Table(
        [[Paragraph("TỔNG THANH TOÁN:", total_style), Paragraph(_money(final_amount), total_right_style)]],
        colWidths=[11 * cm, 6 * cm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TEAL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def _money(value) -> str:
    try:
        return f"{int(round(float(value))):,} đ"
    except (TypeError, ValueError):
        return f"{value} đ"


def _esc(value) -> str:
    return html.escape("" if value is None else str(value))

