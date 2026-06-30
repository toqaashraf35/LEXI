# lexi/apps/contract_analysis/urls.py
from django.urls import path
from .views import (
    ContractAnalysisView,
    ContractAnalysisHistoryView,
    ContractAnalysisDetailView,
    ContractAnalysisDeleteView,
    ContractAnalysisDeleteAllView,
)

urlpatterns = [
    path('contract-analysis/analyze/', ContractAnalysisView.as_view()),
    path('contract-analysis/history/', ContractAnalysisHistoryView.as_view()),
    path('contract-analysis/history/<int:pk>/', ContractAnalysisDetailView.as_view()),
    path('contract-analysis/history/<int:pk>/delete/', ContractAnalysisDeleteView.as_view()),
    path('contract-analysis/history/delete-all/', ContractAnalysisDeleteAllView.as_view()),
]