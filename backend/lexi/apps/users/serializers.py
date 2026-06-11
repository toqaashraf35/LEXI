from rest_framework import serializers
from datetime import date
import re
from .models import User
from django.core.validators import RegexValidator
from .services.normalization_service import (
    normalize_gender,
    normalize_phone
)

class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            error_messages={
                "required": "البريد الإلكتروني مطلوب",
                "invalid": "البريد الإلكتروني غير صالح"
            }
        )

    birthdate = serializers.DateField(
        write_only=True,
        error_messages={
            "required": "تاريخ الميلاد مطلوب",
            "invalid": "يجب أن يكون عمرك 18 عامًا على الأقل"
        }
    )

    full_name = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "اسم المستخدم مطلوب"
        }
    )

    password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "كلمة المرور مطلوبة"
        }
    )

    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "تأكيد كلمة المرور مطلوب"
        }
    )
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

        extra_kwargs = {
            "email": {
                "validators": []
            }
        }

    def validate_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("البريد الإلكتروني مستخدم بالفعل"
            )
        return value
    
    def validate_phone(self, value):
        value = normalize_phone(value)

        if value:
            pattern = r"^01[0-2,5][0-9]{8}$"

            if not re.match(pattern, value):
                raise serializers.ValidationError(
                    "رقم هاتف مصري غير صالح"
                )

        return value

    def validate_gender(self, value):
        value = normalize_gender(value)

        if value and value not in ["male", "female"]:
            raise serializers.ValidationError(
                "يجب أن يكون الجنس ذكراً أو أنثى"
            )

        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("يجب أن تتكون كلمة المرور من 8 أحرف على الأقل")

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("يجب أن تحتوي كلمة المرور على حرف كبير")

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("يجب أن تحتوي كلمة المرور على رقم")

        return value

    def validate(self, data):
        errors = {}

        if data.get("password") != data.get("confirm_password"):
            errors["password"] = "كلمات المرور غير متطابقة"

        birthdate = data.get("birthdate")
        if birthdate:
            today = date.today()
            age = today.year - birthdate.year - (
                (today.month, today.day) < (birthdate.month, birthdate.day)
            )

            if age < 18:
                errors["birthdate"] = "يجب أن يكون عمرك 18 عامًا على الأقل"

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
            raise serializers.ValidationError("البريد الإلكتروني أو كلمة المرور غير صحيحة.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")
            
        if not user.is_active and not user.is_verified:
             raise serializers.ValidationError("Email is not verified")

        data['user'] = user
        return data  

class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "رمز الهوية مطلوب",
            "blank": "رمز الهوية لا يمكن أن يكون فارغًا",
        }
    )
class CompleteProfileSerializer(serializers.Serializer):

    birthdate = serializers.DateField(
        required=True,
        error_messages={
            "required": "تاريخ الميلاد مطلوب",
            "invalid": "تاريخ الميلاد غير صالح"
        }
    )

    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    gender = serializers.ChoiceField(
        choices=[
            ("male", "male"),
            ("female", "female")
        ],
        required=False,
        allow_null=True
    )

    def validate_birthdate(self, value):
        today = date.today()

        age = today.year - value.year - (
            (today.month, today.day) < (value.month, value.day)
        )

        if age < 18:
            raise serializers.ValidationError("يجب ألا يقل عمر المستخدم عن 18 عامًا")

        return value

    def validate_phone(self, value):
        if not value:
            return value

        value = normalize_phone(value)

        validator = RegexValidator(
            r'^01[0125][0-9]{8}$',
            "رقم هاتف مصري غير صالح"
        )

        validator(value)
        return value
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
            required=True,
            error_messages={
                "required": "البريد الإلكتروني مطلوب",
                "invalid": "البريد الإلكتروني غير صالح"
            }
        )
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("لم يتم العثور على المستخدم")
        return value

class VerifyResetCodeSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "البريد الإلكتروني مطلوب",
            "invalid": "البريد الإلكتروني غير صالح"
        }
    )

    code = serializers.CharField(
        required=True,
        max_length=6,
        error_messages={
            "required": "رمز إعادة التعيين مطلوب",
            "blank": "رمز إعادة التعيين مطلوب",
            # "max_length": "يجب ألا يزيد رمز التحقق عن 6 أرقام"
        }
    )

    def validate_code(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                "رمز إعادة التعيين غير صالح"
            )

        if len(value) != 6:
            raise serializers.ValidationError(
                "يجب أن يتكون رمز إعادة التعيين من 6 أرقام"
            )

        return value

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
            required=True,
            error_messages={
                "required": "البريد الإلكتروني مطلوب",
                "invalid": "البريد الإلكتروني غير صالح"
            }
        )    
    code = serializers.CharField(
            required=True,
            max_length=6,
            error_messages={
                "required": "رمز إعادة التعيين مطلوب",
                "blank": "رمز إعادة التعيين مطلوب",
                # "max_length": "يجب ألا يزيد رمز التحقق عن 6 أرقام"
            }
        )

    def validate_code(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                "رمز إعادة التعيين غير صالح"
            )

        if len(value) != 6:
            raise serializers.ValidationError(
                "يجب أن يتكون رمز إعادة التعيين من 6 أرقام"
            )
        return value
    
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("يجب أن تتكون كلمة المرور من 8 أحرف على الأقل")

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("يجب أن تحتوي كلمة المرور على حرف كبير")

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("يجب أن تحتوي كلمة المرور على رقم")

        return value
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "كلمات المرور غير متطابقة"})
        return data

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "birthdate",
            "gender",
            "date_joined"
        ]

class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "full_name",
            "phone",
            "gender"
        ]

    def validate(self, data):

        forbidden_fields = {
            "email": "البريد الإلكتروني",
            "birthdate": "تاريخ الميلاد"
        }

        for field, label in forbidden_fields.items():

            if field in self.initial_data:
                raise serializers.ValidationError({
                    field: f"لا يمكن تعديل {label}"
                })


        return data

    def validate_phone(self, value):
        value = normalize_phone(value)

        if value:
            pattern = r"^01[0-2,5][0-9]{8}$"

            if not re.match(pattern, value):
                raise serializers.ValidationError("رقم هاتف مصري غير صالح")
        return value

    def validate_gender(self, value):
        value = normalize_gender(value)

        if value and value not in ["male", "female"]:
            raise serializers.ValidationError("يجب أن يكون الجنس ذكراً أو أنثى")
        return value

class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "كلمات المرور غير متطابقة"})

        return data

    def validate_new_password(self, value):

        if len(value) < 8:
            raise serializers.ValidationError(
                "يجب أن تتكون كلمة المرور من 8 احرف على الاقل"
            )

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "يجب أن تحتوي كلمة المرور على حرف كبير"
            )

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("يجب أن تحتوي كلمة المرور على رقم")

        return value
