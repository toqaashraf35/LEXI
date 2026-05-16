from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.pdfbase import pdfmetrics

from reportlab.pdfbase.cidfonts import (
    UnicodeCIDFont
)

from reportlab.lib.pagesizes import A4

import os
import uuid


pdfmetrics.registerFont(
    UnicodeCIDFont('STSong-Light')
)


def generate_contract_pdf(content):

    filename = f"{uuid.uuid4()}.pdf"

    folder = "media/contracts"
    os.makedirs(folder, exist_ok=True)  # 🔥 الحل الأساسي

    filepath = os.path.join(folder, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph(content, styles["BodyText"]))
    story.append(Spacer(1, 12))

    doc.build(story)

    return filepath