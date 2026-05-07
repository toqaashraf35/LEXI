from django.urls import path
from .views import SignupView, VerifyEmailView, ResendVerificationCodeView, GoogleAuthView, CompleteProfileView

urlpatterns = [
    path("auth/signup/", SignupView.as_view()),
    path("auth/verify-email/", VerifyEmailView.as_view()),
    path("auth/resend-verification-code/", ResendVerificationCodeView.as_view()),
    path('auth/google/', GoogleAuthView.as_view()),
    path('profile/complete/', CompleteProfileView.as_view()),
]
