import base64
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature


# Keys

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


# Signatures

def current_date_time():
    return datetime.now()


def __signature_message(username, date_time):
    return (username + " " + date_time.isoformat()).encode('utf-8')


def __signature_padding():
    return padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                       salt_length=padding.PSS.MAX_LENGTH)


def __signature_hash():
    return hashes.SHA256()


def generate_signature(private_key, username, date_time):
    signature = private_key.sign(__signature_message(username=username, date_time=date_time),
                                 __signature_padding(),
                                 __signature_hash())

    return base64.b64encode(signature).decode('utf-8')


def check_signature(public_key, signature, username, date_time):
    try:
        decoded_signature = base64.b64decode(signature)
        public_key.verify(decoded_signature,
                          __signature_message(
                              username=username, date_time=date_time),
                          __signature_padding(),
                          __signature_hash())
        return True
    except InvalidSignature:
        return False


# Messages

def __message_padding():
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )


def encrypt_message(sender_private_key, receiver_public_key, sender, receiver, time, message):
    encrypted = receiver_public_key.encrypt(
        message.encode('utf-8'), __message_padding())
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_message(receiver_private_key, sender_public_key, ciphertext):
    decoded_ciphertext = base64.b64decode(ciphertext)
    return receiver_private_key.decrypt(decoded_ciphertext, __message_padding()).decode('utf-8')
