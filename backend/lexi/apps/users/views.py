from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from .services.auth_service import create_user
from django.contrib.auth import get_user_model
from .models import EmailVerification
from .services.email_service import resend_verification_code
class SignupView(APIView):

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        user = create_user(serializer.validated_data)

        return Response({
            "status": "success",
            "message": "User created successfully. Please verify your email.",
            "data": {
                "email": user.email,
                "full_name": user.full_name
            }
        }, status=status.HTTP_201_CREATED)
    
User = get_user_model()
class VerifyEmailView(APIView):

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({
                "status": "error",
                "message": "Email and code are required",
                "errors": ["email and code are required"]
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found",
                "errors": ["invalid email"]
            }, status=status.HTTP_404_NOT_FOUND)

        verification = EmailVerification.objects.filter(
            user=user,
            is_used=False
        ).order_by('-created_at').first()

        if not verification:
            return Response({
                "status": "error",
                "message": "No verification code found",
                "errors": ["request new code"]
            }, status=status.HTTP_400_BAD_REQUEST)

        if verification.code != code:
            return Response({
                "status": "error",
                "message": "Invalid verification code",
                "errors": ["wrong code"]
            }, status=status.HTTP_400_BAD_REQUEST)

        if verification.is_expired():
            return Response({
                "status": "error",
                "message": "Code expired",
                "errors": ["expired code"]
            }, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.is_verified = True
        user.save()

        verification.is_used = True
        verification.save()

        return Response({
            "status": "success",
            "message": "Email verified successfully",
            "data": {
                "user_id": user.id,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)

class ResendVerificationCodeView(APIView):

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({
                "status": "error",
                "message": "User already verified"
            }, status=status.HTTP_400_BAD_REQUEST)

        resend_verification_code(user)

        return Response({
            "status": "success",
            "message": "Verification code resent successfully"
        }, status=status.HTTP_200_OK)