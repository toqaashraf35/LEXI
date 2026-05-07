from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_verification_email(email, code):

    html_content = render_to_string(
        "verify_email.html",
        {"code": code}
    )

    msg = EmailMultiAlternatives(
        "Verify your email",
        "Verify your email",
        settings.EMAIL_HOST_USER,
        [email]
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_reset_password_email(email, code):

    html_content = render_to_string(
        "reset_password.html",
        {"code": code}
    )

    msg = EmailMultiAlternatives(
        "Reset your password",
        "Reset your password",
        settings.EMAIL_HOST_USER,
        [email]
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()