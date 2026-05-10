from datetime import date

def complete_profile(user, validated_data):
    birthdate = validated_data["birthdate"]

    # Age check
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
    user.profile_completed = True   # ← correct field name
    user.is_active = True
    user.save()

    return user