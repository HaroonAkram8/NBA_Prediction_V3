from cryptography.fernet import Fernet
from src.globals import KEY_PATH

def generate_key():
    key = Fernet.generate_key()

    with open(KEY_PATH, 'wb') as file:
        file.write(key)

def load_key():
    key = None

    with open(KEY_PATH, 'rb') as file:
        key = file.read()

    return Fernet(key)