import re

def normalize_field(text):
    return str(text).strip()

def normalize_key(key):
    return re.sub(r"\s+", " ", str(key).strip())

def fill_contract_template(template, fields):
    for key, value in fields.items():
        key = normalize_key(key)
        value = normalize_field(value)
        template = template.replace(f"[{key}]", value)

    return template

