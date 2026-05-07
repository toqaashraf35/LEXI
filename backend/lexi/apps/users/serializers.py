from rest_framework import serializers
from datetime import date
import re
from .models import User
from django.core.validators import RegexValidator

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

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active and not user.is_verified:
            raise serializers.ValidationError("Email is not verified")

        data['user'] = user
        return data  
class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)

class CompleteProfileSerializer(serializers.Serializer):
    birth_date = serializers.DateField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gender = serializers.ChoiceField(
        choices=['male', 'female'],
        required=False,
        allow_null=True
    )

    def validate_birth_date(self, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("User must be at least 18 years old")
        return value

    def validate_phone(self, value):
        if value:
            validator = RegexValidator(r'^01[0125][0-9]{8}$', "Invalid Egyptian phone number")
            validator(value)
        return value