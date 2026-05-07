from django.urls import path
from .views import SignupView, VerifyEmailView, ResendVerificationCodeView

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("verify-email/", VerifyEmailView.as_view()),
    path("resend-verification-code/", ResendVerificationCodeView.as_view()),
]
