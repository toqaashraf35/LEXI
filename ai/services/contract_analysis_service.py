# ai/services/contract_analysis_service.py
import pickle
import json
import re
import io
import os
import fitz
import pytesseract
from PIL import Image
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODELS_DIR = Path(__file__).resolve().parent.parent / 'contract_analysis' / 'arabic_legal_final_model'

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ── Lazy model loading ────────────────────────────────────────
_ridge_model = None
_best_thresholds_ridge = None
_mlb = None
_le_risk_type = None
_RISK_TYPE_AR = None
_y = None


def _load(filename):
    with open(MODELS_DIR / filename, 'rb') as f:
        return pickle.load(f)


def _load_models():
    global _ridge_model, _best_thresholds_ridge, _mlb, _le_risk_type, _RISK_TYPE_AR, _y
    if _ridge_model is None:
        _ridge_model           = _load('ridge_model_best.pkl')
        _best_thresholds_ridge = _load('ridge_thresholds.pkl')
        _mlb                   = _load('mlb.pkl')
        _le_risk_type          = _load('le_risk_type.pkl')
        _RISK_TYPE_AR          = _load('risk_type_ar_map.pkl')
        _y                     = _load('y.pkl')


# ── Text extraction ───────────────────────────────────────────

def normalize_arabic(text):
    text = re.sub(r'[\u200e\u200f\u200b\u200c\u200d\ufeff]', '', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub('[إأآ]', 'ا', text)
    # Remove short isolated Latin-letter OCR garbage (1-4 letters surrounded by spaces)
    text = re.sub(r'(?<![A-Za-z])[A-Za-z]{1,4}(?![A-Za-z])', '', text)
    # Clean up extra spaces left behind
    text = re.sub(r'\s{2,}', ' ', text)
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


# ── Clause extraction ─────────────────────────────────────────
CLAUSE_EXTRACTION_PROMPT = """أنت أداة استخراج بنود قانونية دقيقة جدًا. مهمتك الوحيدة هي تقسيم نص عقد عربي إلى بنوده وأحكامه المنفصلة.

قواعد صارمة يجب الالتزام بها:
1. اقرأ النص الكامل للعقد المُعطى.
2. حدد وافصل كل بند أو مادة أو حكم أو التزام أو شرط أو حق أو مسؤولية أو جزاء أو نص تعاقدي مستقل.
3. كل بند يجب ألا يتجاوز 3-4 جمل — إذا كان البند طويلاً قسّمه لبنود أصغر.
4. تعامل مع جميع أنماط الترقيم والتنسيق.
5. احتفظ بالنص العربي الأصلي تمامًا كما ورد دون أي تغيير في المحتوى القانوني.
6. ممنوع تلخيص النص أو إعادة الصياغة أو حذف أو إضافة أي كلمة من المحتوى القانوني الفعلي.
7. أرجع كل بند كعنصر منفصل في القائمة.
8. تجاهل تمامًا: أرقام الصفحات، الترويسات، التذييلات، التوقيعات، الأختام.
9. هذا النص ناتج عن تحويل ضوئي (OCR) لمستند ممسوح ضوئيًا، لذا قد تظهر فيه رموز أو حروف لاتينية أو أحرف عشوائية ناتجة عن أخطاء المسح الضوئي (مثل أسماء فارغة، تواقيع، أختام، أو خطوط منقطة). احذف هذه الرموز والأحرف اللاتينية العشوائية التي لا تمثل كلمات حقيقية أو معنى قانوني، واستبدلها بمسافة أو احذفها تمامًا، بشرط ألا تحذف أي محتوى قانوني عربي حقيقي.
10. إذا واجهت اسمًا فارغًا مكتوبًا كنقاط أو خط فاصل (مثل: ".......false" أو رموز غريبة بدلاً من اسم الطرف)، اتركه كما هو أو استبدله بـ "غير مذكور" دون حذف بقية البند.

أرجع النتيجة بصيغة JSON فقط:
{"clauses": [{"clause_id": 1, "text": "..."}, {"clause_id": 2, "text": "..."}]}

نص العقد:
\"\"\"
{contract_text}
\"\"\""""

def chunk_text(text, max_chars=12000, overlap=500):
    if len(text) <= max_chars:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + max_chars])
        start += max_chars - overlap
    return chunks


def extract_clauses_with_llm(contract_text):
    prompt = CLAUSE_EXTRACTION_PROMPT.replace('{contract_text}', contract_text)
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {'role': 'system', 'content': 'أنت أداة استخراج نصوص قانونية. لا تجب إلا بصيغة JSON.'},
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.0,
        max_tokens=8000,
        response_format={'type': 'json_object'},
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw).get('clauses', [])
    except json.JSONDecodeError:
        return []


# ── ML prediction ─────────────────────────────────────────────
def predict_clause(clause, contract_type='عام', contract_subtype='عام'):
    _load_models()
    full_text     = f'[{contract_type}] [{contract_subtype}] {clause}'
    X_transformed = _ridge_model.named_steps['tfidf'].transform([full_text])
    estimators    = _ridge_model.named_steps['clf'].estimators_
    y_columns     = list(_y.columns)

    raw_pred = []
    for i, col in enumerate(y_columns):
        if col == 'risk_type_label':
            raw_pred.append(estimators[i].predict(X_transformed)[0])
        else:
            score = estimators[i].decision_function(X_transformed)[0]
            t     = _best_thresholds_ridge[col]
            raw_pred.append(1 if score >= t else 0)

    risk       = int(raw_pred[0])
    party_cols = list(_mlb.classes_)
    parties    = [party_cols[i] for i, v in enumerate(raw_pred[1:1+len(party_cols)]) if v == 1]

    risk_type_idx = int(raw_pred[-1])
    risk_type_en  = _le_risk_type.classes_[risk_type_idx]
    risk_type_ar  = _RISK_TYPE_AR.get(risk_type_en, risk_type_en)

    return {
        'risk':         risk,
        'risk_parties': parties      if risk == 1 else [],
        'risk_type':    risk_type_ar if risk == 1 else None,
    }


# ── LLM explanation ───────────────────────────────────────────
SYSTEM_PROMPT = (
    'أنت مساعد قانوني متخصص في تبسيط البنود التعاقدية العربية لغير المختصين. '
    'مهمتك الوحيدة هي تحليل بند تعاقدي معين بناءً فقط على نص البند والتصنيفات المعطاة. '
    'لا تضف أي افتراضات قانونية غير مدعومة بالنص. '
    'لا تستشهد بقوانين أو مواد قانونية محددة لم تُذكر في النص. '
    'اكتب بلغة عربية فصحى واضحة ومفهومة لغير المتخصصين في القانون. '
    'أجب دائمًا بصيغة JSON صالحة فقط بدون أي نص إضافي.'
)


def explain_clause_risk(clause, parties, risk_type_ar):
    parties_str = '، '.join(parties) if parties else 'غير محدد'
    user_prompt = f"""
البند التعاقدي: \"{clause}\"
الأطراف المتأثرة: {parties_str}
نوع الخطر: {risk_type_ar}

أرجع تحليلك بصيغة JSON فقط بالشكل التالي بالضبط:
{{
  "explanation": "شرح موجز (2-4 جمل) يوضح لماذا يُعتبر هذا البند خطرًا وما الآثار القانونية أو المالية أو التشغيلية المحتملة وأي طرف هو الأكثر تأثرًا",
  "risk_level": "منخفض أو متوسط أو مرتفع فقط — اختر واحدة بناءً على مدى خطورة البند",
  "recommendation": "جملة أو جملتان تخبر المستخدم بما يجب الانتباه له أو فعله قبل التوقيع"
}}

قواعد صارمة:
- اعتمد فقط على نص البند والتصنيفات المذكورة.
- لا تضف أي افتراضات أو مخاطر غير مذكورة أو غير مفهومة من النص.
- إذا كان الخطر بسيطًا فاجعل risk_level = "منخفض".
- إذا كان البند وصفيًا أو تنظيميًا فقط ولا يتضمن التزامًا أو مسؤولية أو أثرًا قانونيًا أو ماليًا أو تشغيليًا واضحًا، فاذكر في الشرح أنه بند وصفي أو تنظيمي فقط.
- لا تحاول اختلاق مبررات لوجود خطر.
- risk_level يجب أن يكون إحدى القيم: منخفض، متوسط، مرتفع فقط.
- لا تضف أي نص خارج JSON.
"""
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': user_prompt}
        ],
        temperature=0.3,
        max_tokens=500,
        response_format={'type': 'json_object'},
    )
    raw = response.choices[0].message.content.strip()
    try:
        parsed = json.loads(raw)
        return {
            'explanation':    parsed.get('explanation', ''),
            'risk_level':     parsed.get('risk_level', 'متوسط'),
            'recommendation': parsed.get('recommendation', ''),
        }
    except json.JSONDecodeError:
        return {'explanation': raw, 'risk_level': 'متوسط', 'recommendation': ''}

# ── Main pipeline ─────────────────────────────────────────────
def analyze_contract(file_path, contract_type='عام', contract_subtype='عام'):
    raw_text = extract_text(file_path)

    chunks = chunk_text(raw_text)
    all_clauses = []
    clause_counter = 1
    for chunk in chunks:
        extracted = extract_clauses_with_llm(chunk)
        for c in extracted:
            all_clauses.append({
                'clause_id': clause_counter,
                'text': c.get('text', '').strip()
            })
            clause_counter += 1

    analyzed = []
    for c in all_clauses:
        prediction = predict_clause(c['text'], contract_type, contract_subtype)
        explanation = risk_level = recommendation = None
        is_risky = prediction['risk'] == 1

        if is_risky:
            parties = prediction["risk_parties"] if is_risky else []
            llm_result     = explain_clause_risk(c['text'], parties, prediction['risk_type'])
            explanation    = llm_result['explanation']
            risk_level     = llm_result['risk_level']
            recommendation = llm_result['recommendation']
        else:
            parties = []

        analyzed.append({
            'clause_id':      c['clause_id'],
            'clause_text':    c['text'],
            'risk':           'نعم' if is_risky else 'لا',
            'risk_type':      prediction['risk_type'] if is_risky else None,
            'risk_parties':   parties,
            'explanation':    explanation,
            'risk_level':     risk_level,
            'recommendation': recommendation,
        })

    total = len(analyzed)
    risky = sum(1 for c in analyzed if c['risk'] == 'نعم')

    return {
        'contract_analysis': analyzed,
        'summary': {
            'total_clauses': total,
            'risky_clauses': risky,
            'safe_clauses':  total - risky,
        }
    }