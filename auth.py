"""Password hashing — the single place bcrypt is touched.

Kept as two pure functions so the rest of the app never imports a hashing
library directly, and so the hash/verify contract can be exercised without
going through HTTP. Chosen per ADR-0002 (email + password, a hash stored).
"""

import base64
import hashlib

import bcrypt


def _prepared(password: str) -> bytes:
    """bcrypt silently caps its input at 72 bytes; collapse the password to a
    fixed-width digest first (the standard pre-hash) so every character still
    counts and there is no length ceiling to police at the route.
    """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(password: str) -> str:
    """Return a slow-KDF (bcrypt) hash of ``password``, safe to store as text."""
    return bcrypt.hashpw(_prepared(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """True when ``password`` matches the stored ``password_hash``."""
    try:
        return bcrypt.checkpw(_prepared(password), password_hash.encode("utf-8"))
    except ValueError:
        # Malformed / non-bcrypt hash (e.g. a corrupted row): treat as no match.
        return False
