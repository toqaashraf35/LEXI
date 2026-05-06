from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

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