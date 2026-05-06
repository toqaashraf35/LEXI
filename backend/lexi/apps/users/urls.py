from django.urls import path
from .views import SignupView, VerifyEmailView

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("verify-email/", VerifyEmailView.as_view()),
]
