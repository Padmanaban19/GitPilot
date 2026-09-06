import base64

import pytest
from nacl.public import PrivateKey, SealedBox

from gitpilot.github.encryption import encrypt_secret


def test_encrypt_secret_can_be_decrypted():
    private_key = PrivateKey.generate()
    public_key = private_key.public_key

    public_key_b64 = base64.b64encode(bytes(public_key)).decode("utf-8")
    secret = "super-secret-value"

    encrypted = encrypt_secret(public_key_b64, secret)

    encrypted_bytes = base64.b64decode(encrypted)
    sealed_box = SealedBox(private_key)

    decrypted = sealed_box.decrypt(encrypted_bytes).decode("utf-8")

    assert decrypted == secret

def test_encrypt_secret_rejects_invalid_public_key():
    with pytest.raises(ValueError, match="Invalid GitHub public key"):
        encrypt_secret("not-a-valid-key", "secret")