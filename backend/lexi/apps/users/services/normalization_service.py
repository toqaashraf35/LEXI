from ....common.normalizers import normalize_arabic_numbers

def normalize_phone(phone):
    if not phone:
        return phone

    phone = phone.strip()

    phone = normalize_arabic_numbers(phone)

    phone = phone.replace(" ", "")

    return phone


def normalize_gender(gender):
    if not gender:
        return gender

    gender = gender.strip().lower()

    gender_map = {
        "male": "male",
        "ذكر": "male",
        "رجل": "male",

        "female": "female",
        "أنثى": "female",
        "انثى": "female",
        "بنت": "female",
        "امرأة": "female"
    }

    return gender_map.get(gender, gender)