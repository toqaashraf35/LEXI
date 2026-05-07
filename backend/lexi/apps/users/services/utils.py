from django.utils import timezone
from ..models import EmailVerification
import random

def generate_verification_code(user):
    code = str(random.randint(100000, 999999))
    expires_at = timezone.now() + timezone.timedelta(minutes=10)

    EmailVerification.objects.create(
        user=user,
        code=code,
        expires_at=expires_at
    )
    return code

def get_first_error(errors):
    return list(errors.values())[0][0]

def generate_verification_code():
    return str(random.randint(100000, 999999))