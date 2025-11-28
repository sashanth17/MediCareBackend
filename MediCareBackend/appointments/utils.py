# utils.py
import re

def normalize_phone(raw_phone: str) -> str:
    """
    Normalize a phone number for consistent lookup:
    - strip whitespace
    - keep a leading '+' if present
    - remove any other non-digit characters
    Returns empty string if input is falsy.
    """
    if not raw_phone:
        return ""
    p = raw_phone.strip()
    if p.startswith("+"):
        return "+" + re.sub(r"\D", "", p[1:])
    return re.sub(r"\D", "", p)
