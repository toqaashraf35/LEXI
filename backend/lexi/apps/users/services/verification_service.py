from ..models import EmailVerification


def verify_email_code(user, code):

    verification = EmailVerification.objects.filter(
        user=user,
        is_used=False
    ).order_by("-created_at").first()

    if not verification:
        raise ValueError("No verification code found")

    if verification.code != code:
        raise ValueError("Invalid verification code")

    if verification.is_expired():
        raise ValueError("Code expired")

    return verification

def activate_user(user, verification):

    user.is_active = True
    user.is_verified = True
    user.save()

    verification.is_used = True
    verification.save()