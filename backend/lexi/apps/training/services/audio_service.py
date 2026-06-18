import os
import subprocess
import uuid
import librosa
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from django.conf import settings

MODELS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / 'ai' / 'video_training'

def extract_audio(video_path):
    audio_path = f"temp_audio_{uuid.uuid4().hex}.mp3"  # ← unique name
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