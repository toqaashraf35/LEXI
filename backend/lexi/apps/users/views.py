from datetime import date
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    CompleteProfileSerializer,
    ForgotPasswordSerializer,
    GoogleAuthSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    SignupSerializer,
    VerifyResetCodeSerializer,
    UserProfileSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer
)
from .services.auth_service import (
    create_google_user,
    create_user,
    resend_verification_code,
)
from .services.google_service import (
    verify_google_token,
)
from .services.password_service import (
    create_reset_password_code,
    reset_user_password,
    verify_reset_password_code,
    change_password
)
from .services.profile_service import (
    complete_profile,
    update_profile,
    delete_profile
)

from lexi.common.responses import (
    success_response,
    error_response,
    get_first_error
)

from .services.verification_service import (
    activate_user,
    verify_email_code,
)



User = get_user_model()

class SignupView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                get_first_error(serializer.errors),
                serializer.errors
            )

        user = create_user(serializer.validated_data)

        return success_response(
            "User created successfully. Please verify your email.",
            {
                "email": user.email,
                "full_name": user.full_name
            },
            status.HTTP_201_CREATED
        )

class VerifyEmailView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return error_response(
                "Email and code are required"
            )

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return error_response(
                "User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            verification = verify_email_code(user, code)

        except ValueError as e:
            return error_response(str(e))

        activate_user(user, verification)

        return success_response(
            "Email verified successfully",
            {
                "user_id": user.id,
                "email": user.email
            }
        )

class ResendVerificationCodeView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")

        if not email:
            return error_response(
                "Email is required"
            )

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return error_response(
                "User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if user.is_verified:
            return error_response(
                "User already verified"
            )

        resend_verification_code(user)

        return success_response(
            "Verification code resent successfully",
            {
                "user_id": user.id,
                "email": user.email
            }
        )

class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                get_first_error(serializer.errors),
                serializer.errors
            )

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return success_response(
            "Login successful",
            {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "profile_completed": user.profile_completed,
                "token": str(refresh.access_token),
                "refresh": str(refresh)
            }
        )

class GoogleAuthView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = GoogleAuthSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                get_first_error(serializer.errors),
                serializer.errors
            )

        token = serializer.validated_data["id_token"]

        try:
            user_info = verify_google_token(token)

        except ValueError as e:
            return error_response(
                str(e),
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        email = user_info["email"]

        user = User.objects.filter(email=email).first()

        if not user:
            user = create_google_user(user_info)

        elif not user.is_verified:
            user.is_verified = True
            user.save()

        refresh = RefreshToken.for_user(user)

        return success_response(
            "Login successful",
            {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "profile_completed": user.profile_completed,
                "token": str(refresh.access_token),
                "refresh": str(refresh)
            }
        )

class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.profile_completed:
            return error_response("Profile already completed")

        serializer = CompleteProfileSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                get_first_error(serializer.errors),
                serializer.errors
            )

        try:
            complete_profile(user, serializer.validated_data)
        except ValueError as e:
            return error_response(str(e))

        return success_response("Profile completed successfully")

class ForgotPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ForgotPasswordSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return error_response(
                get_first_error(serializer.errors),
                serializer.errors
            )

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return error_response(
                "User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if not user.has_usable_password():
            return error_response(
                "This account uses Google Sign-In"
            )

        create_reset_password_code(user)

        return success_response(
            "Password reset code sent successfully"
        )

class VerifyResetCodeView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = VerifyResetCodeSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return error_response(
                get_first_error(serializer.errors),
                serializer.errors
            )

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return error_response(
                "User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            verify_reset_password_code(user, code)

        except ValueError as e:
            return error_response(str(e))

        return success_response(
            "Code verified successfully"
        )

class ResetPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ResetPasswordSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return error_response(
                get_first_error(serializer.errors),
                serializer.errors
            )

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return error_response(
                "User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            reset_user_password(
                user,
                code,
                new_password
            )

        except ValueError as e:
            return error_response(str(e))

        return success_response(
            "Password reset successfully"
        )
    
class MyProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserProfileSerializer(request.user)

        return success_response(
            "Profile fetched successfully",
            serializer.data
        )

class UpdateProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return error_response(
                get_first_error(serializer.errors),
                serializer.errors
            )

        user = update_profile(
            request.user,
            serializer.validated_data
        )

        return success_response(
            "Profile updated successfully",
            UserProfileSerializer(user).data
        )
    
class DeleteProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):

        delete_profile(request.user)

        return success_response(
            "Profile deleted successfully"
        )
    
class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return error_response(
                get_first_error(serializer.errors),
                serializer.errors
            )

        try:
            change_password(
                request.user,
                serializer.validated_data["old_password"],
                serializer.validated_data["new_password"]
            )

        except ValueError as e:
            return error_response(str(e))

        return success_response(
            "Password changed successfully"
        )