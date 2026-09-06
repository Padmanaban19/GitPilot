import base64

from nacl.exceptions import CryptoError
from nacl.public import PublicKey, SealedBox


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using a GitHub repository public key."""
    try:
        key = PublicKey(base64.b64decode(public_key))
        sealed_box = SealedBox(key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    except (ValueError, CryptoError) as exc:
        raise ValueError("Invalid GitHub public key.") from exc

    return base64.b64encode(encrypted).decode("utf-8")