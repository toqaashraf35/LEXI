from .audio_service import analyze_audio
from .video_service import analyze_video
from .report_service import generate_report


def run_full_analysis(video_path):
    audio_results = analyze_audio(video_path)
    body_results = analyze_video(video_path)
    report = generate_report(audio_results, body_results)

    return {
        "audio_analysis": audio_results,
        "body_analysis": body_results,
        "report": report
    }