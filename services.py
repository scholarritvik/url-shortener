# services.py

import re
from database import (
    insert_url_and_get_id,
    update_short_code,
    get_url_by_code,
    increment_clicks
)

BASE62 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


# ---------- URL VALIDATION ----------
def is_valid_url(url: str) -> bool:
    """
    Basic URL validation.
    Requires http:// or https://
    """
    pattern = re.compile(
        r'^(https?:\/\/)'
        r'([\w\-]+\.)+[\w\-]+'
        r'([\/\w\-._~:?#[\]@!$&\'()*+,;=%]*)?$'
    )
    return bool(pattern.match(url))


# ---------- BASE62 ENCODING ----------
def encode_base62(num: int, length: int = 7) -> str:
    base = len(BASE62)
    encoded = []

    if num == 0:
        encoded.append(BASE62[0])

    while num > 0:
        encoded.append(BASE62[num % base])
        num //= base

    encoded_str = ''.join(reversed(encoded))

    # Pad to fixed length
    return encoded_str.rjust(length, BASE62[0])


# ---------- SHORT URL CREATION ----------
def create_short_url(original_url: str) -> str:
    """
    Main service function.
    Returns short_code for a valid URL.
    """
    if not is_valid_url(original_url):
        raise ValueError("Invalid URL, please enter proper URL")

    # Step 1: Insert URL, get ID
    url_id = insert_url_and_get_id(original_url)

    # Step 2: Encode ID
    short_code = encode_base62(url_id)

    # Step 3: Store short_code
    update_short_code(url_id, short_code)

    return short_code


# ---------- REDIRECT HELPERS ----------
def resolve_short_code(code: str):
    """
    Fetch original URL and increment clicks.
    """
    row = get_url_by_code(code)

    if not row:
        return None

    original_url, clicks = row
    increment_clicks(code, clicks)

    return original_url