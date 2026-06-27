import json
import os
from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

CLAUSE_EXTRACTION_PROMPT = """أنت أداة استخراج بنود قانونية دقيقة جدًا. مهمتك الوحيدة هي تقسيم نص عقد عربي إلى بنوده وأحكامه المنفصلة.

قواعد صارمة يجب الالتزام بها:
1. اقرأ النص الكامل للعقد المُعطى.
2. حدد وافصل كل بند أو مادة أو حكم أو التزام أو شرط أو حق أو مسؤولية أو جزاء أو نص تعاقدي مستقل.
3. كل بند يجب ألا يتجاوز 3-4 جمل — إذا كان البند طويلاً قسّمه لبنود أصغر.
4. تعامل مع جميع أنماط الترقيم والتنسيق.
5. احتفظ بالنص العربي الأصلي تمامًا كما ورد دون أي تغيير.
6. ممنوع تلخيص النص أو إعادة الصياغة أو حذف أو إضافة أي كلمة.
7. أرجع كل بند كعنصر منفصل في القائمة.
8. تجاهل تمامًا: أرقام الصفحات، الترويسات، التذييلات، التوقيعات، الأختام.

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
            {'role': 'system', 'content': 'أنت أداة استخراج نصوص قانونية. لا تجب إلا بصيغة JSON صالحة فقط.'},
            {'role': 'user',   'content': prompt}
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