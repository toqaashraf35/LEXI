from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
import arabic_reshaper
import os


# ── Font registration ────────────────────────────────────────────────
_FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_FONT_PATH = os.path.join(_FONTS_DIR, "NotoNaskhArabic-Regular.ttf")

if not os.path.exists(_FONT_PATH):
    raise FileNotFoundError(
        f"Arabic font not found at: {_FONT_PATH}\n"
        "Place NotoNaskhArabic-Regular.ttf inside a 'fonts/' folder"
    )

pdfmetrics.registerFont(TTFont("Arabic", _FONT_PATH))


# ── Arabic helper (ONLY reshaping, no bidi) ───────────────────────────
def format_arabic(text: str) -> str:
    if not text or not text.strip():
        return text
    return arabic_reshaper.reshape(text)


# ── PDF Builder ───────────────────────────────────────────────────────
def create_contract_pdf(contract_name: str, contract_content: str) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    # Title style
    title_style = ParagraphStyle(
        name="ArabicTitle",
        fontName="Arabic",
        fontSize=16,
        leading=30,
        alignment=TA_CENTER,
    )

    # Body style (IMPORTANT: RTL alignment only)
    body_style = ParagraphStyle(
        name="ArabicBody",
        fontName="Arabic",
        fontSize=12,
        leading=28,
        alignment=TA_RIGHT,
    )

    elements = []

    # ── Title ─────────────────────────────────────────────
    elements.append(
        Paragraph(format_arabic(contract_name), title_style)
    )

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%"))
    elements.append(Spacer(1, 20))

    # ── IMPORTANT FIX: single Paragraph instead of many ────
    formatted_lines = [
        format_arabic(line)
        for line in contract_content.split("\n")
        if line.strip()
    ]

    full_text = "<br/>".join(formatted_lines)

    elements.append(Paragraph(full_text, body_style))

    # ── Build PDF ──────────────────────────────────────────
    doc.build(elements)

    buffer.seek(0)
    buffer.name = "contract.pdf"
    return buffer