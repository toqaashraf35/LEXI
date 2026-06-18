from django.urls import path
from .views import TrainingAnalysisView, TrainingDetailView, TrainingHistoryView

urlpatterns = [
    path("training/analyze/", TrainingAnalysisView.as_view()),
    path("training/history/", TrainingHistoryView.as_view()),
    path("training/history/<int:pk>/", TrainingDetailView.as_view()),
]