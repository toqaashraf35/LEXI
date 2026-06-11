from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

def verify_google_token(token):
    try:
        print("GOOGLE_CLIENT_ID:", settings.GOOGLE_CLIENT_ID)

        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=[
                settings.GOOGLE_CLIENT_ID,
                "407408718192.apps.googleusercontent.com"
            ]
        )

        if not idinfo.get("email_verified"):
            raise ValueError("لم يتم التحقق من بريد جوجل الإلكتروني")

        return {
            "email": idinfo["email"],
            "full_name": idinfo.get("name", ""),
        }

    except ValueError as e:
        raise ValueError(str(e))