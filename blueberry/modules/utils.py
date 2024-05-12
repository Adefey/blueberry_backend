import re
import hashlib
from modules.config import (
    AUTH_SECRET,
)
import time


def validate_string(string: str) -> bool:
    if len(string) < 5:
        return False
    pattern = re.compile(r"[a-zA-Z0-9()!?@#^&$%_/.]*$")
    return bool(pattern.match(string))


def create_token(username: str) -> str:
    buf = f"{AUTH_SECRET}+{username}+{time.time()}"
    result = hashlib.sha256(buf.encode()).hexdigest()
    return result
