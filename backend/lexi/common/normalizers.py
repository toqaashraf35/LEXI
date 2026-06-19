def normalize_arabic_numbers(value):
    if value is None:
        return value

    value = str(value)

    english_numbers = "0123456789"
    arabic_numbers = "٠١٢٣٤٥٦٧٨٩"

    table = str.maketrans(english_numbers, arabic_numbers)

    return value.translate(table)