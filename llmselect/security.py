from cryptography.fernet import Fernet


class KeyEncryptionService:
    """
    Provides encryption utilities for API keys using Fernet symmetric encryption.
    """

    def __init__(self, key: str):
        self._fernet = Fernet(key)

    def encrypt(self, value: str) -> bytes:
        return self._fernet.encrypt(value.encode())

    def decrypt(self, token: bytes) -> str:
        return self._fernet.decrypt(token).decode()
