from rest_framework import serializers
from datetime import date
import re
from .models import User

class SignupSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "full_name",
            "email",
            "password",
            "confirm_password",
            "phone",
            "birthdate",
            "gender"
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_phone(self, value):
        if value:
            pattern = r"^01[0-2,5][0-9]{8}$"
            if not re.match(pattern, value):
                raise serializers.ValidationError("Invalid Egyptian phone number")
        return value

    def validate_gender(self, value):
        if value and value not in ["male", "female"]:
            raise serializers.ValidationError("Gender must be male or female")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain uppercase letter")

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Password must contain a number")

        return value

    def validate(self, data):
        errors = {}

        if data.get("password") != data.get("confirm_password"):
            errors["password"] = "Passwords do not match"

        birthdate = data.get("birthdate")
        if birthdate:
            today = date.today()
            age = today.year - birthdate.year - (
                (today.month, today.day) < (birthdate.month, birthdate.day)
            )

            if age < 18:
                errors["birthdate"] = "You must be at least 18 years old"

        if errors:
            raise serializers.ValidationError(errors)

        return data