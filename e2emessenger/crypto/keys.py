import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

KEY_FILE_NAME = 'key.private'


def generate_keypair():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def save_keypair(private_key, loc):
    private_contents = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                 encryption_algorithm=serialization.NoEncryption())

    key_path = os.path.join(loc, KEY_FILE_NAME)
    with open(key_path, 'w', encoding="utf-8") as private_key_file:
        private_key_file.write(private_contents.decode("utf-8"))
    os.chmod(key_path, 0o600)


def load_keypair(loc):
    key_path = os.path.join(loc, KEY_FILE_NAME)
    with open(key_path, 'rb') as private_key_file:
        return serialization.load_pem_private_key(private_key_file.read(), password=None)
