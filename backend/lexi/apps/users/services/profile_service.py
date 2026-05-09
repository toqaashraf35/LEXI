def complete_profile(user, validated_data):

    user.birthdate = validated_data["birthdate"]
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