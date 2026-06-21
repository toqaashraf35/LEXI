import io
import html as html_module
from django.conf import settings

_FONT_DIR = getattr(settings, 'ARABIC_FONT_DIR', '/backend/lexi/apps/contracts/services/fonts')
_FONT_REGULAR = f'{_FONT_DIR}/NotoNaskhArabic-Regular.ttf'
_FONT_BOLD    = f'{_FONT_DIR}/NotoNaskhArabic-Regular.ttf'


def _build_css() -> str:
    return f"""
    @font-face {{
        font-family: 'Amiri';
        src: url('{_FONT_REGULAR}') format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    @font-face {{
        font-family: 'Amiri';
        src: url('{_FONT_BOLD}') format('truetype');
        font-weight: bold;
        font-style: normal;
    }}

    @page {{
        size: A4;
        margin: 2.5cm 2cm 2cm 2cm;
    }}

    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-variant-numeric: tabular-nums;
        -moz-font-feature-settings: "lnum" 1;
        -webkit-font-feature-settings: "lnum" 1;
        font-feature-settings: "lnum" 1;
    
    }}

    body {{
        font-family: 'Amiri', serif;
        font-size: 13pt;
        line-height: 2;
        color: #1a1a1a;
        direction: rtl;
        unicode-bidi: embed;
        text-align: right;
    }}
        
    .contract-title {{
        text-align: center;
        font-size: 20pt;
        font-weight: bold;
        margin-bottom: 0.8cm;
        padding-bottom: 0.4cm;
        border-bottom: 1.5px solid #333;
    }}

    .contract-body {{
        margin-top: 0.5cm;
    }}

    .spacer {{
        height: 0.4cm;
    }}

    p {{
        text-align: justify;
        text-align-last: right;
        margin-bottom: 0.5cm;
    }}

    .filled-value {{
        font-weight: bold;
        text-decoration: underline;
        text-decoration-color: #555;
    }}
    """

def _content_to_html(content: str) -> str:

    paragraphs = []
    current_lines = []

    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            current_lines.append(html_module.escape(stripped))
        else:
            if current_lines:
                paragraphs.append('<p>' + '<br>'.join(current_lines) + '</p>')
                current_lines = []
            else:
                paragraphs.append('<div class="spacer"></div>')

    if current_lines:
        paragraphs.append('<p>' + '<br>'.join(current_lines) + '</p>')

    return '\n'.join(paragraphs)

def _build_html(contract_name: str, filled_content: str) -> str:
    css  = _build_css()
    body = _content_to_html(filled_content)

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <style>{css}</style>
</head>
<body>
    <div class="contract-title">{html_module.escape(contract_name)}</div>
    <div class="contract-body">
        {body}
    </div>
</body>
</html>"""

def generate_pdf_bytes(contract_name: str, filled_content: str) -> bytes:
    try:
        import weasyprint
    except ImportError:
        raise ImportError(
            "weasyprint غير مثبّت. شغّل: pip install weasyprint"
        )

    html_content = _build_html(contract_name, filled_content)

    pdf_buffer = io.BytesIO()
    weasyprint.HTML(string=html_content).write_pdf(pdf_buffer)

    return pdf_buffer.getvalue()