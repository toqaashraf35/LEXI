# ai/services/training_service.py
import os
import subprocess
import uuid
import librosa
import numpy as np
import pandas as pd
import joblib
import cv2
import mediapipe as mp
from fer import FER
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from typer import prompt

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

MODELS_DIR = Path(__file__).resolve().parent.parent / 'video_training'

X_body = ["lm_0_y", "lm_1_y", "lm_11_x", "lm_12_x", "lm_23_z"]
X_emotion = [
    "happy_mean", "sad_mean", "angry_mean",
    "dominant_happy_percent",
    "dominant_fear_percent",
    "dominant_neutral_percent"
]
X_hybrid = X_body + X_emotion

BODY_LABELS = [
    "head_stability_label",
    "posture_openness_label",
    "body_stability_label",
    "body_confidence_label"
]
EMOTION_LABELS = [
    "emotional_state_label",
    "emotional_confidence_label"
]

mp_pose = mp.solutions.pose
detector = FER(mtcnn=True)


# ── Audio analysis ──────────────────────────────────────────────
def extract_audio(video_path):
    audio_path = f"temp_audio_{uuid.uuid4().hex}.mp3"
    command = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "mp3",
        "-ar", "44100", "-ac", "1",
        audio_path, "-y"
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return audio_path


def analyze_audio(video_path):
    audio_path = extract_audio(video_path)
    try:
        y, sr = librosa.load(audio_path, sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)

        X = pd.DataFrame([mfcc_mean])

        model_path = MODELS_DIR / 'xgboost_model.pkl'
        model = joblib.load(str(model_path))
        y_pred = model.predict(X)

        return {
            "speech_rate_score": float(y_pred[0][0]),
            "energy_score": float(y_pred[0][1]),
            "confidence_score": float(y_pred[0][2]),
            "pitch_mean": float(y_pred[0][3]),
            "pitch_std": float(y_pred[0][4]),
        }
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


# ── Video / body / emotion analysis ────────────────────────────
def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    pose = mp_pose.Pose(static_image_mode=False)
    body_data = []
    emotion_data = []

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        fps = 30

    interval = 2
    sample_every = fps * interval
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % sample_every != 0:
            frame_count += 1
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pose_result = pose.process(frame_rgb)
        if pose_result.pose_landmarks:
            lm = pose_result.pose_landmarks.landmark
            body_data.append({
                "lm_0_y": lm[0].y,
                "lm_1_y": lm[1].y,
                "lm_11_x": lm[11].x,
                "lm_12_x": lm[12].x,
                "lm_23_z": lm[23].z
            })

        try:
            emotions = detector.detect_emotions(frame)
        except Exception:
            emotions = []

        if emotions:
            probs = emotions[0]["emotions"]
            dominant = max(probs, key=probs.get)
            emotion_data.append({
                "happy_mean": probs.get("happy", 0),
                "sad_mean": probs.get("sad", 0),
                "angry_mean": probs.get("angry", 0),
                "dominant_happy_percent": 1 if dominant == "happy" else 0,
                "dominant_fear_percent": 1 if dominant == "fear" else 0,
                "dominant_neutral_percent": 1 if dominant == "neutral" else 0
            })

        frame_count += 1

    cap.release()
    pose.close()

    if len(body_data) == 0:
        raise ValueError("No body/pose detected in video")
    if len(emotion_data) == 0:
        raise ValueError("No emotion detected in video")

    body_df = pd.DataFrame(body_data)
    emotion_df = pd.DataFrame(emotion_data)

    body_mean = body_df.mean().to_dict()
    emotion_mean = emotion_df.mean().to_dict()
    final_features = {**body_mean, **emotion_mean}
    final_df = pd.DataFrame([final_features])

    for col in X_hybrid:
        if col not in final_df.columns:
            final_df[col] = 0.0

    models_path = MODELS_DIR / 'all_xgb_models.pkl'
    models = joblib.load(str(models_path))

    predictions = {}
    for label, model_data in models.items():
        model = model_data["model"]
        encoder = model_data["encoder"]

        if label in BODY_LABELS:
            X_input = final_df[X_body]
        elif label in EMOTION_LABELS:
            X_input = final_df[X_emotion]
        else:
            X_input = final_df[X_hybrid]

        pred_encoded = model.predict(X_input)[0]
        pred_label = encoder.inverse_transform([pred_encoded])[0]
        predictions[label] = pred_label

    return predictions


# ── Report generation ───────────────────────────────────────────
LABELS_AR = {
    "Stable Head": "ثبات جيد للرأس",
    "Unstable Head": "عدم ثبات الرأس",

    "Open Posture": "وضعية جسم منفتحة",
    "Closed Posture": "وضعية جسم منغلقة",

    "Stable Body": "استقرار جيد للجسم",
    "Unstable Body": "عدم استقرار الجسم",

    "High Body Confidence": "ثقة عالية في لغة الجسد",
    "Low Body Confidence": "ثقة منخفضة في لغة الجسد",

    "Neutral / Controlled": "حالة انفعالية متزنة",
    "Positive": "حالة إيجابية",
    "Negative": "حالة سلبية",

    "Emotionally Balanced": "اتزان عاطفي",
    "Emotionally Unstable": "عدم اتزان عاطفي",

    "Moderately Confident Speaker": "متحدث يتمتع بثقة متوسطة",
    "Highly Confident Speaker": "متحدث واثق",
    "Low Confidence Speaker": "متحدث منخفض الثقة",

    "Highly Engaged": "تفاعل مرتفع",
    "Moderately Engaged": "تفاعل متوسط",
    "Low Engaged": "تفاعل منخفض",

    "High Confidence": "ثقة عالية",
    "Medium Confidence": "ثقة متوسطة",
    "Low Confidence": "ثقة منخفضة",

    "Balanced": "متوازن",
    "Neutral": "محايد",
    "Positive Emotion": "مشاعر إيجابية",
    "Negative Emotion": "مشاعر سلبية",

    "Open": "منفتح",
    "Closed": "منغلق",

    "Stable": "مستقر",
    "Unstable": "غير مستقر"
}

def generate_report(audio_results, body_results):
    body_results = {
    k: LABELS_AR.get(v, v)
    for k, v in body_results.items()
}
    prompt = f"""
أنت خبير في تقييم مهارات الإلقاء والعروض التقديمية للمحامين والمتحدثين.

ستصلك نتائج تحليل صوت ولغة جسد، ومهمتك كتابة تقرير احترافي.

قواعد إلزامية:

- اكتب باللغة العربية الفصحى فقط.
- ممنوع استخدام أي كلمة إنجليزية أو أي لغة أخرى.
- ممنوع كتابة أي أحرف لاتينية أو صينية أو رموز غريبة.
- إذا وجدت مصطلحًا غير عربي فاستبدله بالمقابل العربي المناسب.
- لا تذكر الدرجات أو الأرقام داخل التقرير.
- لا تخترع معلومات غير موجودة.
- اجعل التقرير مبنيًا فقط على النتائج التالية.

نتائج تحليل الصوت:

معدل الكلام:
{audio_results["speech_rate_score"]:.2f}

الطاقة الصوتية:
{audio_results["energy_score"]:.2f}

الثقة في الصوت:
{audio_results["confidence_score"]:.2f}

متوسط طبقة الصوت:
{audio_results["pitch_mean"]:.2f}

تذبذب طبقة الصوت:
{audio_results["pitch_std"]:.2f}

نتائج تحليل لغة الجسد:

ثبات الرأس:
{body_results.get("head_stability_label", "غير متوفر")}

وضعية الجسم:
{body_results.get("posture_openness_label", "غير متوفر")}

استقرار الجسم:
{body_results.get("body_stability_label", "غير متوفر")}

ثقة لغة الجسد:
{body_results.get("body_confidence_label", "غير متوفر")}

الحالة العاطفية:
{body_results.get("emotional_state_label", "غير متوفر")}

الاتزان العاطفي:
{body_results.get("emotional_confidence_label", "غير متوفر")}

الثقة العامة:
{body_results.get("overall_confidence_label", "غير متوفر")}

التفاعل:
{body_results.get("engagement_label", "غير متوفر")}

اكتب التقرير بهذا الترتيب فقط:

## شخصية المتحدث

## مستوى الثقة

## الحالة النفسية

## نقاط القوة
- ...
- ...
- ...

## نقاط الضعف
- ...
- ...
- ...

## نصائح للتحسين
- ...
- ...
- ...

راجع الإجابة قبل إرسالها.

إذا احتوت على أي كلمة غير عربية فأعد صياغتها بالكامل بالعربية.
"""

    chat_completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content":
            "أنت كاتب تقارير احترافية باللغة العربية الفصحى فقط. يمنع استخدام أي لغة أخرى أو أي أحرف لاتينية."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.2,
    top_p=0.9,
)

    return chat_completion.choices[0].message.content


# ── Main pipeline ───────────────────────────────────────────────
def run_full_analysis(video_path):
    audio_results = analyze_audio(video_path)
    body_results = analyze_video(video_path)
    report = generate_report(audio_results, body_results)

    return {
        "audio_analysis": audio_results,
        "body_analysis": body_results,
        "report": report
    }