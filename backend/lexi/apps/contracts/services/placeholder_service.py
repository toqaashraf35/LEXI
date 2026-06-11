import re

def extract_placeholders(text):
    return re.findall(r"\[(.*?)\]", text)