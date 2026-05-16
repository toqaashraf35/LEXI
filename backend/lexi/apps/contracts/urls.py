from django.urls import path
from .views import ContractDetailsView, GenerateContractView

urlpatterns = [
    path("<int:contract_id>/",ContractDetailsView.as_view()),
    path("generate/",GenerateContractView.as_view())
]