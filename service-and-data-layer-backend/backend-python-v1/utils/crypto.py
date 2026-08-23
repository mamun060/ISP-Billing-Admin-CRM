import base64
import hashlib
from django.conf import settings

from cryptography.fernet import Fernet


def _get_fernet():
    # derive a 32-byte key from SECRET_KEY
    secret = settings.SECRET_KEY.encode("utf-8")
    digest = hashlib.sha256(secret).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_text(plain: str) -> str:
    if plain is None:
        return None
    f = _get_fernet()
    return f.encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_text(token: str) -> str:
    if token is None:
        return None
    f = _get_fernet()
    try:
        return f.decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        return None
