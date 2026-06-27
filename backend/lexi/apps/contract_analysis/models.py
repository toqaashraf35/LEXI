# lexi/apps/contract_analysis/models.py
from django.db import models
from django.conf import settings


class ContractAnalysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contract_analyses'
    )
    file_url = models.URLField()              # Cloudinary URL
    file_name = models.CharField(max_length=255)
    contract_type = models.CharField(max_length=100, default='عام')
    contract_subtype = models.CharField(max_length=100, default='عام')
    total_clauses = models.IntegerField(default=0)
    risky_clauses = models.IntegerField(default=0)
    safe_clauses = models.IntegerField(default=0)
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.file_name} - {self.created_at}"