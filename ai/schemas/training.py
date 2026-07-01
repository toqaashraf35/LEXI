from pydantic import BaseModel
from typing import Dict, Any


class AudioAnalysis(BaseModel):
    speech_rate_score: float
    energy_score: float
    confidence_score: float
    pitch_mean: float
    pitch_std: float


class TrainingAnalysisResponse(BaseModel):
    audio_analysis: Dict[str, Any]
    body_analysis: Dict[str, Any]
    report: str