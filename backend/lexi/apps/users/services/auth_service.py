from ..models import User

def create_user(validated_data):
    user = User.objects.create(
        full_name=validated_data["full_name"],
        email=validated_data["email"],
        phone=validated_data.get("phone"),
        birthdate=validated_data["birthdate"],
        gender=validated_data.get("gender"),
        is_active=False,
        is_verified=False,
    )

    user.set_password(validated_data["password"])
    user.save()

    return user
