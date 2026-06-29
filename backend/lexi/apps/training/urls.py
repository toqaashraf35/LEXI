from django.urls import path
from .views import (
    TrainingAnalysisView,
    TrainingHistoryView,
    TrainingDetailView,
    TrainingDeleteView,
    TrainingDeleteAllView,
)

urlpatterns = [
    path("training/analyze/", TrainingAnalysisView.as_view()),
    path("training/history/", TrainingHistoryView.as_view()),
    path("training/history/<int:pk>/", TrainingDetailView.as_view()),
    path("training/history/<int:pk>/delete/", TrainingDeleteView.as_view()),
    path("training/history/delete-all/", TrainingDeleteAllView.as_view()),
]