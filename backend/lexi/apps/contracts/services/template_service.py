import re
from ....common.normalizers import normalize_arabic_numbers

def fill_contract_template(template: str, data: dict):

    def replace(match):
        key = match.group(1).strip()

        value = data.get(key, f"[{key}]")

        print("RAW VALUE:", key, value)   # 👈 مهم جدًا

        value = str(value)
        value = normalize_arabic_numbers(value)

        print("AFTER:", value)  # 👈

        return value

    return re.sub(r"\[(.*?)\]", replace, template)