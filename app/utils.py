"""
Utility helper functions for URL Shortener.
Lab 4: URL Validation
Lab 5: Base62 Short Code Generation
"""
import hashlib
import re
import secrets
import string
from urllib.parse import urlparse

# Base62 character set: 10 digits + 26 lowercase + 26 uppercase = 62 characters
BASE62_CHARACTERS = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE62_SET = set(BASE62_CHARACTERS)

# Regular expression for validating well-formed hostname
HOSTNAME_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9]"  # First character of hostname
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"  # Subdomains
    r"[a-zA-Z]{2,63}$"  # Top-level domain (TLD)
)

# Regular expression for custom short codes (4-16 alphanumeric chars or hyphens)
SHORT_CODE_REGEX = re.compile(r"^[a-zA-Z0-9_-]{4,16}$")


def is_valid_url(url: str) -> tuple[bool, str]:
    """
    Validates whether a string is a legitimate, well-formed HTTP/HTTPS URL.
    Returns:
        tuple[bool, str]: (is_valid, error_reason)
    """
    if not url or not isinstance(url, str):
        return False, "URL cannot be empty."

    cleaned_url = url.strip()

    if len(cleaned_url) > 2048:
        return False, "URL exceeds maximum permitted length of 2048 characters."

    try:
        parsed = urlparse(cleaned_url)
    except Exception:
        return False, "Malformed URL format."

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported URL scheme '{parsed.scheme}'. Only 'http://' and 'https://' are permitted."

    if not parsed.netloc:
        return False, "URL must include a valid host/domain name (e.g., example.com)."

    host = parsed.netloc.split(":")[0].lower()

    # Allow localhost and loopback IP for local cloud development/testing
    if host in ("localhost", "127.0.0.1", "::1"):
        return True, ""

    # Check against domain regex or IPv4 pattern
    is_ipv4 = bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host))
    if not is_ipv4 and not HOSTNAME_REGEX.match(host):
        return False, f"Invalid domain structure '{host}'. Must be a valid domain name."

    return True, ""


def generate_short_code(length: int = 6) -> str:
    """
    Generates a cryptographically secure random Base62 short code.
    Default length 6 gives 62^6 ≈ 56.8 billion combinations.
    """
    return "".join(secrets.choice(BASE62_CHARACTERS) for _ in range(length))


def encode_base62(num: int) -> str:
    """
    Encodes an integer into a Base62 string representation.
    Used for mapping sequential database IDs to compact URL keys.
    """
    if num == 0:
        return BASE62_CHARACTERS[0]

    digits = []
    base = len(BASE62_CHARACTERS)
    while num > 0:
        digits.append(BASE62_CHARACTERS[num % base])
        num //= base
    return "".join(reversed(digits))


def hash_url_to_code(url: str, length: int = 6) -> str:
    """
    Deterministically computes a Base62 short code from an input URL using SHA-256.
    Ensures identical URLs produce the same short code when desired.
    """
    digest = hashlib.sha256(url.strip().encode("utf-8")).hexdigest()
    # Take first 12 hex characters and convert to integer
    num = int(digest[:12], 16)
    code = encode_base62(num)
    return code[:length].ljust(length, "a")


def is_valid_custom_code(code: str) -> tuple[bool, str]:
    """
    Validates a user-provided custom alias/short code.
    Must be 4-16 alphanumeric characters, dashes or underscores.
    """
    if not code:
        return False, "Short code cannot be empty."
    if not SHORT_CODE_REGEX.match(code):
        return False, "Custom code must be 4 to 16 characters long and contain only letters, numbers, hyphens, or underscores."
    return True, ""
