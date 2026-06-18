from django.db import models
from django.conf import settings


class TrainingAnalysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='training_analyses'
    )
    video_url = models.URLField()
    audio_analysis = models.JSONField()
    body_analysis = models.JSONField()
    report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.created_at}"