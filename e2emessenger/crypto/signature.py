import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


def current_date_time():
    return datetime.now()


def __signature_message(username, date_time):
    return (username + " " + date_time.isoformat()).encode('utf-8')


def __padding():
    return padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                       salt_length=padding.PSS.MAX_LENGTH)


def __hash():
    return hashes.SHA256()


def generate_signature(private_key, username, date_time):
    signature = private_key.sign(__signature_message(username=username, date_time=date_time),
                                 __padding(),
                                 __hash())

    return base64.b64encode(signature).decode('utf-8')


def check_signature(public_key, signature, username, date_time):
    try:
        decoded_signature = base64.b64decode(signature)
        public_key.verify(decoded_signature,
                          __signature_message(
                              username=username, date_time=date_time),
                          __padding(),
                          __hash())
        return True
    except InvalidSignature:
        return False
