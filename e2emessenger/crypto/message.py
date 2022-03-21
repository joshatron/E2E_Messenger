import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def __padding():
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )


def encrypt(public_key, message):
    encrypted = public_key.encrypt(message.encode('utf-8'), __padding())
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt(private_key, ciphertext):
    decoded_ciphertext = base64.b64decode(ciphertext)
    return private_key.decrypt(decoded_ciphertext, __padding()).decode('utf-8')
