import cv2
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from django.conf import settings

MODELS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / 'ai' / 'video_training'

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


def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)

    body_data = []
    emotion_data = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        body_features = {
            "lm_0_y": np.random.rand(),
            "lm_1_y": np.random.rand(),
            "lm_11_x": np.random.rand(),
            "lm_12_x": np.random.rand(),
            "lm_23_z": np.random.rand()
        }
        body_data.append(body_features)

        emotion_features = {
            "happy_mean": np.random.rand(),
            "sad_mean": np.random.rand(),
            "angry_mean": np.random.rand(),
            "dominant_happy_percent": np.random.rand(),
            "dominant_fear_percent": np.random.rand(),
            "dominant_neutral_percent": np.random.rand()
        }
        emotion_data.append(emotion_features)

    cap.release()

    if not body_data or not emotion_data:
        raise ValueError("Video is empty or could not be processed")

    body_df = pd.DataFrame(body_data)
    emotion_df = pd.DataFrame(emotion_data)

    final_features = {**body_df.mean().to_dict(), **emotion_df.mean().to_dict()}
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