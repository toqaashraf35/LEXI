import re

def render_contract(template: str, data: dict):
    def replace(match):
        key = match.group(1)
        return str(data.get(key, f"[{key}]"))

    return re.sub(r"\[(.*?)\]", replace, template)