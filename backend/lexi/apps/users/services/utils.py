from django.utils import timezone
from ..models import EmailVerification
import random
from rest_framework.response import Response

def generate_verification_code(user):
    code = str(random.randint(100000, 999999))
    expires_at = timezone.now() + timezone.timedelta(minutes=10)

    EmailVerification.objects.create(
        user=user,
        code=code,
        expires_at=expires_at
    )
    return code

