def normalize_arabic_numbers(value):
    arabic_numbers = "٠١٢٣٤٥٦٧٨٩"
    english_numbers = "0123456789"

    translation_table = str.maketrans(
        arabic_numbers,
        english_numbers
    )

    return value.translate(translation_table)