from datetime import date

def complete_profile(user, validated_data):
    birthdate = validated_data["birthdate"]

    today = date.today()
    age = today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

    if age < 18:
        user.is_active = False
        user.save()
        raise ValueError("User must be at least 18 years old")

    user.birthdate = birthdate
    user.phone = validated_data.get("phone") or user.phone
    user.gender = validated_data.get("gender") or user.gender
    user.profile_completed = True
    user.is_active = True
    user.save()

    return user

def update_profile(user, validated_data):
    for key, value in validated_data.items():
        setattr(user, key, value)
    user.save()
    return user

def delete_profile(user):
    user.delete()