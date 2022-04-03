from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

KEY_FILE_NAME = 'key.private'


def generate_keypair():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def export_keypair(private_key):
    return private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                     format=serialization.PrivateFormat.TraditionalOpenSSL,
                                     encryption_algorithm=serialization.NoEncryption()).decode('utf-8')


def import_keypair(keypair_contents):
    return serialization.load_pem_private_key(keypair_contents.encode('utf-8'), password=None)


def export_public_key(public_key):
    return public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                   format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')


def import_public_key(public_key_contents):
    return serialization.load_pem_public_key(public_key_contents.encode('utf-8'))
