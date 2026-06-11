from ..models import EmailVerification

def verify_email_code(user, code):
    verification = EmailVerification.objects.filter(
        user=user,
        is_used=False
    ).order_by("-created_at").first()

    if not verification:
        raise ValueError("لم يتم العثور على رمز التحقق")

    if verification.code != code:
        raise ValueError("رمز التحقق غير صالح")

    if verification.is_expired():
        raise ValueError("انتهت صلاحية الرمز")

    return verification

def activate_user(user, verification):
    user.is_active = True
    user.is_verified = True
    user.save()

    verification.is_used = True
    verification.save()