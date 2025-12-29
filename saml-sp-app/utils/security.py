import os
from cryptography.fernet import Fernet

FERNET_KEY = os.environ["LOG_ENC_KEY"]
cipher = Fernet(FERNET_KEY)

def encrypt_log(value: str) -> str:
    """Encrypt a string before storing in DB."""
    return cipher.encrypt(value.encode()).decode()

def decrypt_log(value: str) -> str:
    """Decrypt a string retrieved from DB."""
    return cipher.decrypt(value.encode()).decode()
