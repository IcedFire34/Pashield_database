from cryptography.fernet import Fernet
from .config import settings
import base64

def get_fernet_key():
    key = settings.ENCRYPTION_KEY.encode()
    key = base64.urlsafe_b64encode(key.ljust(32)[:32])
    return key

def encrypt_data(data: str) -> str:
    fernet = Fernet(get_fernet_key())
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    try:
        fernet = Fernet(get_fernet_key())
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")