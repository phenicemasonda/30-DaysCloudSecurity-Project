# utils/logger.py

from utils.crypto import encrypt
from config import Config
from datetime import datetime

def secure_log(message: str):
    timestamp = datetime.utcnow().isoformat()
    entry = f"{timestamp} | {message}\n"
    encrypted = encrypt(entry)

    with open(Config.LOG_FILE, "ab") as f:
        f.write(encrypted + b"\n")
