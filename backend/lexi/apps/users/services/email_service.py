from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from ..models import EmailVerification
from .utils import generate_verification_code

def send_verification_email(email, code):

    subject = "Verify your email"

    html_content = render_to_string("verify_email.html", {
        "code": code
    })

    msg = EmailMultiAlternatives(
        subject,
        "Verify your email",
        settings.EMAIL_HOST_USER,
        [email] 
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()

def resend_verification_code(user):
    EmailVerification.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)

    code = generate_verification_code()

    EmailVerification.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10),
        is_used=False
    )

    send_verification_email(user.email, code)

    return code