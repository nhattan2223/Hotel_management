from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle

from services.invoice_fonts import (
    FONT_BOLD,
    FONT_BOLD_ITALIC,
    FONT_REGULAR,
)


TEAL = colors.HexColor("#00B4A6")
DARK = colors.HexColor("#1A2E35")
GRID = colors.HexColor("#C8E6E4")
LIGHT_TEAL = colors.HexColor("#E0F7F5")


def styles() -> dict:
    return {
        "hotel": ParagraphStyle(
            "InvoiceHotel",
            fontName=FONT_BOLD,
            fontSize=18,
            leading=22,
            textColor=TEAL,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "title": ParagraphStyle(
            "InvoiceTitle",
            fontName=FONT_BOLD,
            fontSize=16,
            leading=20,
            textColor=DARK,
            alignment=TA_CENTER,
            spaceAfter=5,
        ),
        "sub": ParagraphStyle(
            "InvoiceSub",
            fontName=FONT_REGULAR,
            fontSize=9.5,
            leading=13,
            textColor=DARK,
            alignment=TA_CENTER,
        ),
        "cell": ParagraphStyle(
            "InvoiceCell",
            fontName=FONT_REGULAR,
            fontSize=9,
            leading=12,
            textColor=DARK,
        ),
        "cell_bold": ParagraphStyle(
            "InvoiceCellBold",
            fontName=FONT_BOLD,
            fontSize=9,
            leading=12,
            textColor=DARK,
        ),
        "cell_right": ParagraphStyle(
            "InvoiceCellRight",
            fontName=FONT_REGULAR,
            fontSize=9,
            leading=12,
            textColor=DARK,
            alignment=TA_RIGHT,
        ),
        "header": ParagraphStyle(
            "InvoiceHeader",
            fontName=FONT_BOLD,
            fontSize=9,
            leading=12,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "section": ParagraphStyle(
            "InvoiceSection",
            fontName=FONT_BOLD,
            fontSize=11,
            leading=14,
            textColor=TEAL,
            spaceBefore=6,
            spaceAfter=4,
        ),
        "thanks": ParagraphStyle(
            "InvoiceThanks",
            fontName=FONT_BOLD_ITALIC,
            fontSize=11,
            leading=14,
            textColor=TEAL,
            alignment=TA_CENTER,
        ),
    }

