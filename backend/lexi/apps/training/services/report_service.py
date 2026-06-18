from groq import Groq
from django.conf import settings


def generate_report(audio_results, body_results):
    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""
أنت محلل متخصص في تقييم أداء المتحدثين والمحامين.

قواعد صارمة يجب اتباعها بدقة تامة:
- اكتب التقرير باللغة العربية الفصحى فقط وبدون أي استثناء
- ممنوع منعاً باتاً استخدام أي كلمة أجنبية مهما كانت (إنجليزية، فرنسية، صينية، فيتنامية، أو أي لغة أخرى)
- إذا أردت التعبير عن مفهوم أجنبي، ابحث عن مقابله العربي الصحيح
- مثال: بدلاً من "personality" اكتب "الشخصية"، بدلاً من "Crossing" اكتب "تقاطع"، بدلاً من "engagement" اكتب "الانخراط"
- إذا لم تجد مقابلاً عربياً، صف المعنى بالعربية
- لا تستخدم أي حرف لاتيني أو صيني أو من لغات أخرى غير العربية في أي مكان في ردك

تحليل الصوت:
- معدل الكلام: {audio_results['speech_rate_score']:.2f}
- الطاقة الصوتية: {audio_results['energy_score']:.2f}
- الثقة في الصوت: {audio_results['confidence_score']:.2f}
- متوسط طبقة الصوت: {audio_results['pitch_mean']:.2f}
- تذبذب طبقة الصوت: {audio_results['pitch_std']:.2f}

تحليل لغة الجسد:
- ثبات الرأس: {body_results.get('head_stability_label')}
- وضعية الجسم: {body_results.get('posture_openness_label')}
- استقرار الجسم: {body_results.get('body_stability_label')}
- ثقة لغة الجسد: {body_results.get('body_confidence_label')}

تحليل المشاعر:
- الحالة العاطفية: {body_results.get('emotional_state_label')}
- الثقة العاطفية: {body_results.get('emotional_confidence_label')}
- الثقة العامة: {body_results.get('overall_confidence_label')}
- مستوى التفاعل: {body_results.get('engagement_label')}

اكتب تقريرًا احترافيًا منظمًا باللغة العربية الفصحى فقط يتضمن:
١. شخصية المتحدث
٢. مستوى الثقة
٣. الحالة النفسية
٤. نقاط القوة
٥. نقاط الضعف
٦. نصائح للتحسين

تعليمات مهمة:
- استخدم اللغة العربية الفصحى فقط
- لا تستخدم أي كلمات أجنبية
- اجعل التقرير واضحًا ومنظمًا ومهنيًا
"""

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )

    return chat_completion.choices[0].message.content