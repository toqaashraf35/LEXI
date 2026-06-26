import cv2
import numpy as np
import pandas as pd
import joblib
import mediapipe as mp
from fer import FER
from pathlib import Path

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

# Initialize once — not inside the loop
mp_pose = mp.solutions.pose
detector = FER(mtcnn=True)


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

    interval = 2  # seconds
    sample_every = fps * interval
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Same sampling logic used during training
        if frame_count % sample_every != 0:
            frame_count += 1
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ==========================
        # BODY FEATURES (MediaPipe)
        # ==========================
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

        # ==========================
        # EMOTION FEATURES (FER)
        # ==========================
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

    # Load models - same pattern as before
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