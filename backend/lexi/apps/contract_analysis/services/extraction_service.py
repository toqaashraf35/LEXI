import fitz
import pytesseract
from PIL import Image
import io
import re
import arabic_reshaper
from bidi.algorithm import get_display

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def fix_arabic_text(text):
    """Fix reversed Arabic text from PDFs with wrong encoding."""
    try:
        reshaped = arabic_reshaper.reshape(text)
        fixed = get_display(reshaped)
        return fixed
    except Exception:
        return text


def normalize_arabic(text):
    # Remove Arabic direction marks
    text = re.sub(r'[\u200e\u200f\u200b\u200c\u200d\ufeff]', '', text)
    # Remove other control characters  
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Normalize alef variants
    text = re.sub('[إأآ]', 'ا', text)
    return text


def extract_text_from_pdf(pdf_path):
    """Always use OCR for Arabic PDFs — avoids encoding issues."""
    doc = fitz.open(pdf_path)
    full_text = []

    for page in doc:
        # Render page as high-res image
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes('png')
        img = Image.open(io.BytesIO(img_bytes))

        # OCR with Arabic + English
        custom_config = r'--oem 3 --psm 6 -l ara+eng'
        text = pytesseract.image_to_string(img, config=custom_config)
        full_text.append(text)

    doc.close()
    return normalize_arabic('\n'.join(full_text))


def extract_text_from_image(image_path):
    img = Image.open(image_path)
    
    # Convert to RGB if needed (handles PNG with transparency, etc.)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize if image is too small - improves OCR accuracy
    width, height = img.size
    if width < 1000:
        scale = 1000 / width
        img = img.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
    
    custom_config = r'--oem 3 --psm 6 -l ara+eng'
    text = pytesseract.image_to_string(img, config=custom_config)
    return normalize_arabic(text)


def extract_text(file_path):
    ext = str(file_path).lower().split('.')[-1]
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ('png', 'jpg', 'jpeg', 'tiff', 'bmp'):
        return extract_text_from_image(file_path)
    else:
        raise ValueError(f'Unsupported file type: .{ext}')