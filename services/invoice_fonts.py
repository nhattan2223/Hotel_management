from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


FONT_REGULAR = "InvoiceFont"
FONT_BOLD = "InvoiceFont-Bold"
FONT_ITALIC = "InvoiceFont-Italic"
FONT_BOLD_ITALIC = "InvoiceFont-BoldItalic"


def register_fonts() -> None:
    if FONT_REGULAR in pdfmetrics.getRegisteredFontNames():
        return

    candidates = [
        {
            FONT_REGULAR: r"C:\Windows\Fonts\arial.ttf",
            FONT_BOLD: r"C:\Windows\Fonts\arialbd.ttf",
            FONT_ITALIC: r"C:\Windows\Fonts\ariali.ttf",
            FONT_BOLD_ITALIC: r"C:\Windows\Fonts\arialbi.ttf",
        },
        {
            # macOS system fonts
            FONT_REGULAR: "/System/Library/Fonts/Supplemental/Arial.ttf",
            FONT_BOLD: "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            FONT_ITALIC: "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
            FONT_BOLD_ITALIC: "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
        },
        {
            # Linux DejaVu fonts
            FONT_REGULAR: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            FONT_BOLD: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            FONT_ITALIC: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
            FONT_BOLD_ITALIC: "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        },
    ]

    for group in candidates:
        if all(Path(path).exists() for path in group.values()):
            for name, path in group.items():
                pdfmetrics.registerFont(TTFont(name, path))
            return

    # Keep ReportLab usable on systems without TrueType fonts, though Vietnamese
    # accents may not render correctly with the built-in Helvetica fonts.
    globals()["FONT_REGULAR"] = "Helvetica"
    globals()["FONT_BOLD"] = "Helvetica-Bold"
    globals()["FONT_ITALIC"] = "Helvetica-Oblique"
    globals()["FONT_BOLD_ITALIC"] = "Helvetica-BoldOblique"

