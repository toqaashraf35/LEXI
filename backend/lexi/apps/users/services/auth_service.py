from ..models import User, EmailVerification
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
    )

    user.set_password(validated_data["password"])
    user.save()

    code = generate_verification_code()

    EmailVerification.objects.create(
        user=user,
        code=code
    )

    send_verification_email(user.email, code)

    return user