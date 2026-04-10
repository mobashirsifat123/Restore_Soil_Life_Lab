from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

SCRYPT_PREFIX = "scrypt"
SCRYPT_N = 16_384
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32


def _encode_bytes(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _decode_bytes(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )
    return (
        f"{SCRYPT_PREFIX}${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}"
        f"${_encode_bytes(salt)}${_encode_bytes(digest)}"
    )


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False

    try:
        prefix, n, r, p, salt, expected = password_hash.split("$", maxsplit=5)
    except ValueError:
        return False

    if prefix != SCRYPT_PREFIX:
        return False

    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=_decode_bytes(salt),
        n=int(n),
        r=int(r),
        p=int(p),
        dklen=SCRYPT_DKLEN,
    )
    return hmac.compare_digest(digest, _decode_bytes(expected))


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(session_token: str) -> str:
    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()


def generate_recovery_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_recovery_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()
