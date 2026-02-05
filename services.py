# services.py

import re
from datetime import datetime, timedelta
from database import (
    insert_url_and_get_id,
    update_short_code,
    get_url_by_code,
    increment_clicks
)

DEFAULT_EXPIRY_DAYS = 30
MAX_EXPIRY_DAYS = 90
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
def create_short_url(original_url: str, user_expiry: str | None = None) -> str:
    if not is_valid_url(original_url):
        raise ValueError("Invalid URL. Please include http:// or https://")

    expires_at = calculate_expiry(user_expiry)

    # Step 1: Insert URL, get ID
    url_id = insert_url_and_get_id(original_url, expires_at)

    # Step 2: Encode ID
    short_code = encode_base62(url_id)

    # Step 3: Store short_code
    update_short_code(url_id, short_code)

    return short_code

# ---------- REDIRECT HELPERS ----------
def resolve_short_code(code: str):
    row = get_url_by_code(code)

    if not row:
        return None, "not_found"

    original_url, clicks, expires_at = row

    if datetime.utcnow() > datetime.fromisoformat(expires_at):
        return None, "expired"

    increment_clicks(code, clicks)
    return original_url, "ok"


# to calculate expiry date 
def calculate_expiry(user_expiry: str | None) -> datetime:
    now = datetime.utcnow()

    if not user_expiry:
        return now + timedelta(days=DEFAULT_EXPIRY_DAYS)

    try:
        expiry_date = datetime.fromisoformat(user_expiry)
    except ValueError:
        raise ValueError("Invalid expiry date format")

    max_allowed = now + timedelta(days=MAX_EXPIRY_DAYS)

    if expiry_date > max_allowed:
        raise ValueError("Expiry cannot exceed 3 months")

    if expiry_date <= now:
        raise ValueError("Expiry must be in the future")

    return expiry_date