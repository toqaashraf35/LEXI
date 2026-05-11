from django.urls import path
from .views import (
    SignupView, 
    VerifyEmailView, 
    ResendVerificationCodeView, 
    GoogleAuthView, 
    CompleteProfileView, 
    LoginView,
    ForgotPasswordView,
    ResetPasswordView,
    VerifyResetCodeView,
    MyProfileView,
    UpdateProfileView,
    DeleteProfileView)

urlpatterns = [
    path("auth/signup/", SignupView.as_view()),
    path("auth/verify-email/", VerifyEmailView.as_view()),
    path("auth/resend-verification-code/", ResendVerificationCodeView.as_view()),
    path('auth/google/', GoogleAuthView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/forgot-password/', ForgotPasswordView.as_view()),       
    path('auth/verify-reset-code/', VerifyResetCodeView.as_view()),
    path('auth/reset-password/', ResetPasswordView.as_view()),
    path('profile/complete/', CompleteProfileView.as_view()),
    path("profile/me/", MyProfileView.as_view()),
    path("profile/update/", UpdateProfileView.as_view()),
    path("profile/delete/", DeleteProfileView.as_view()),
]
