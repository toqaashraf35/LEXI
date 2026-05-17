# import re

# def fill_contract_template(template, fields):

#     for key, value in fields.items():

#         pattern = r"\[" + re.escape(key) + r"\]"

#         template = re.sub(
#             pattern,
#             str(value),
#             template
#         )

#     return template

import re

def normalize_field(text):
    """Normalize a single field value (no newline stripping)."""
    return str(text).strip()

def normalize_key(key):
    """Normalize a field key (collapse all whitespace)."""
    return re.sub(r"\s+", " ", str(key).strip())

def fill_contract_template(template, fields):
    # Do NOT normalize the full template — it destroys newlines
    for key, value in fields.items():
        key = normalize_key(key)
        value = normalize_field(value)
        template = template.replace(f"[{key}]", value)

    return template

