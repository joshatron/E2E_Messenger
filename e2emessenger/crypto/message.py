from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def __padding():
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )


def encrypt(public_key, message):
    return public_key.encrypt(message.encode('utf-8'), __padding())


def decrypt(private_key, ciphertext):
    return private_key.decrypt(ciphertext, __padding()).decode('utf-8')
