from .config import client
from .retrieval import retrieve


def rewrite_query(question, history):

    if not history:
        return question

    history_text = "\n".join(
        f"{'المستخدم' if h['role']=='user' else 'المساعد'}: {h['content']}"
        for h in history[-4:]
    )

    prompt = f"""
بناءً على المحادثة السابقة، أعد صياغة السؤال الأخير ليكون سؤالًا مستقلًا.

المحادثة:

{history_text}

السؤال:

{question}

أعد كتابة السؤال فقط.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
    return response.choices[0].message.content.strip()


def answer(question, history):

    standalone_question = rewrite_query(
        question,
        history
    )

    retrieved = retrieve(
        standalone_question
    )

    context = "\n\n".join(
        r["text"]
        for r in retrieved
    )

    prompt = f"""
أنت مساعد قانوني متخصص في محاكم الأسرة المصرية.

استخدم المعلومات فقط من السياق التالي:

{context}

السؤال:

{question}

أجب بالشكل التالي:

📌 المشكلة

⚖️ الإجراءات المطلوبة

📄 المستندات المطلوبة

⚠️ ملاحظات مهمة

إذا لم تجد معلومة كافية داخل السياق
قل:
لا توجد معلومات كافية.
"""

    messages = [
        {
            "role": "system",
            "content": "أنت مساعد قانوني متخصص."
        }
    ]

    messages.extend(history[-4:])

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
    )

    return response.choices[0].message.content