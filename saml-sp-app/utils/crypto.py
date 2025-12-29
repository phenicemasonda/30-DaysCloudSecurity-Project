# utils/crypto.py

from cryptography.fernet import Fernet
import os

KEY = os.getenv("LOG_ENC_KEY") or Fernet.generate_key()
fernet = Fernet(KEY)

def encrypt(data: str) -> bytes:
    return fernet.encrypt(data.encode())
