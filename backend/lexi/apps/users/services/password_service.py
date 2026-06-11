from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from ..models import PasswordResetCode
from .utils import generate_verification_code
from .email_service import send_reset_password_email

User = get_user_model()
def create_reset_password_code(user):
    PasswordResetCode.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)

    code = generate_verification_code(user)

    PasswordResetCode.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10),
        is_used=False
    )

    send_reset_password_email(user.email, code)

    return code

def verify_reset_password_code(user, code):
    reset = PasswordResetCode.objects.filter(
        user=user,
        is_used=False
    ).order_by("-id").first()

    if not reset:
        raise ValueError("لم يتم العثور على رمز إعادة الضبط")

    if reset.code != code:
        raise ValueError("رمز إعادة تعيين غير صالح")

    if reset.expires_at < timezone.now():
        raise ValueError("انتهت صلاحية الرمز")

    return reset

def reset_user_password(user, code, new_password):
    reset = verify_reset_password_code(user, code)

    user.set_password(new_password)
    user.save()

    reset.is_used = True
    reset.save()

def change_password(user, old_password, new_password):

    if not user.check_password(old_password):
        raise ValueError("كلمة المرور القديمة غير صحيحة")

    user.set_password(new_password)
    user.save()