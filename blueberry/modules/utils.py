import re


def validate_string(string: str) -> bool:
    pattern = re.compile(r"[a-zA-Z0-9()!?@#^&$%_/.]*$")
    return bool(pattern.match(string))
