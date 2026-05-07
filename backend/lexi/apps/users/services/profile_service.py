def complete_profile(user, validated_data):

    user.birthdate = validated_data["birthdate"]
    user.phone = validated_data.get("phone") or user.phone
    user.gender = validated_data.get("gender") or user.gender

    user.is_profile_completed = True
    user.is_active = True

    user.save()

    return user