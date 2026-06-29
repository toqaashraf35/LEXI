from rest_framework import serializers
from .models import TrainingAnalysis


class TrainingAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingAnalysis
        fields = [
            'id',
            'video_url',
            'audio_analysis',
            'body_analysis',
            'report',
            'created_at'
        ]