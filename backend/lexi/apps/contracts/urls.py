from django.urls import path
from .views import ContractDetailsView, GenerateContractView, ContractListView, ServeContractPDFView, ContractHistoryDeleteView,ContractHistoryDetailView, ContractHistoryListView

urlpatterns = [
    path("<int:contract_id>/",ContractDetailsView.as_view()),
    path("", ContractListView.as_view()),
    path("pdf/", ServeContractPDFView.as_view()),
    path("generate/",GenerateContractView.as_view()),
    path("history/", ContractHistoryListView.as_view()),
    path("history/<int:pk>/", ContractHistoryDetailView.as_view()),
    path("history/<int:pk>/delete/", ContractHistoryDeleteView.as_view()),
]