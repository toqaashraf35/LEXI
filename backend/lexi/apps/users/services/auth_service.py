from ..models import User, EmailVerification
from django.utils import timezone
from datetime import timedelta
from .utils import generate_verification_code
from .email_service import send_verification_email

def create_user(validated_data):
    user = User.objects.create(
        full_name=validated_data["full_name"],
        email=validated_data["email"],
        phone=validated_data.get("phone"),
        birthdate=validated_data["birthdate"],
        gender=validated_data.get("gender"),
        is_active=False,
        is_verified=False,
        profile_completed=True,
    )

    user.set_password(validated_data["password"])
    user.save()

    code = generate_verification_code(user)

    send_verification_email(user.email, code)

    return user

def create_google_user(user_data):
    user = User.objects.create(
        email=user_data["email"],
        full_name=user_data["full_name"],
        is_active=True,
        is_verified=True,
        is_google_user=True,
        profile_completed=False,
    )
    user.set_unusable_password()
    user.save()

    return user

def resend_verification_code(user):

    EmailVerification.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)

    code = generate_verification_code(user)

    EmailVerification.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10),
        is_used=False
    )

    send_verification_email(user.email, code)

    return code
