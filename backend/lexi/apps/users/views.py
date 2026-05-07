from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from datetime import date
from .models import User, EmailVerification
from .serializers import GoogleAuthSerializer, CompleteProfileSerializer, SignupSerializer, LoginSerializer
from .services.google_service import verify_google_token
from .services.auth_service import create_user, create_google_user
from .services.utils import get_first_error
from .services.email_service import resend_verification_code

class SignupView(APIView):

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": get_first_error(serializer.errors),
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
            "message": "Verification code resent successfully",
            "data": {
                "user_id": user.id,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)

            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "user_id": user.id,
                    "email": user.email,
                    "profile_completed": user.profile_completed,
                    "token": str(refresh.access_token),
                    "refresh": str(refresh)
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "error",
            "message": get_first_error(serializer.errors)
        }, status=status.HTTP_400_BAD_REQUEST) 
    
class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": get_first_error(),
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['id_token']

        try:
            user_info = verify_google_token(token)
        except ValueError as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)

        email = user_info['email']
        full_name = user_info['full_name']

        user = User.objects.filter(email=email).first()

        if not user:
            user = create_google_user(user_info)
        else:
            if not user.is_verified:
                user.is_verified = True
                user.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            "status": "success",
            "message": "Login successful",
            "data": {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "profile_completed": user.profile_completed, 
                "token": str(refresh.access_token),
                "refresh": str(refresh)
            }
        }, status=status.HTTP_200_OK)
    
class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_profile_completed:
            return Response({
                "status": "error",
                "message": "Profile already completed"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CompleteProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": get_first_error(serializer.errors),
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        birth_date = serializer.validated_data['birth_date']

        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        if age < 18:
            user.is_active = False
            user.save()
            return Response({
                "status": "error",
                "message": "User must be at least 18 years old"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save profile data
        user.birth_date = birth_date
        user.phone = serializer.validated_data.get('phone') or user.phone
        user.gender = serializer.validated_data.get('gender') or user.gender
        user.is_profile_completed = True
        user.is_active = True
        user.save()

        return Response({
            "status": "success",
            "message": "Profile completed successfully"
        }, status=status.HTTP_200_OK)