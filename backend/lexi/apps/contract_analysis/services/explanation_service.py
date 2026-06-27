import json
from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = (
    'أنت مساعد قانوني متخصص في تبسيط البنود التعاقدية العربية لغير المختصين. '
    'اكتب بلغة عربية فصحى واضحة. '
    'أجب دائمًا بصيغة JSON صالحة فقط بدون أي نص إضافي.'
)


def explain_clause_risk(clause, parties, risk_type_ar):
    parties_str = '، '.join(parties) if parties else 'غير محدد'
    user_prompt = f"""
البند التعاقدي: \"{clause}\"
الأطراف المتأثرة: {parties_str}
نوع الخطر: {risk_type_ar}

أرجع JSON بالشكل:
{{
  "explanation": "شرح موجز (2-4 جمل)",
  "risk_level": "منخفض أو متوسط أو مرتفع",
  "recommendation": "جملة أو جملتان للمستخدم قبل التوقيع"
}}
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