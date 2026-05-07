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

def get_first_error(errors):
    return list(errors.values())[0][0]

def error_response(message, errors=None, status_code=400):
    return Response({
        "status": "error",
        "message": message,
        "errors": errors
    }, status=status_code)


def success_response(message, data=None, status_code=200):
    return Response({
        "status": "success",
        "message": message,
        "data": data
    }, status=status_code)