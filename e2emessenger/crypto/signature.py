from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


def current_date_time():
    return datetime.now()


def signature_message(username, date_time):
    return (username + " " + date_time.isoformat()).encode('utf-8')


def generate_signature(private_key, username, date_time):
    return private_key.sign(signature_message(username=username, date_time=date_time),
                            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                        salt_length=padding.PSS.MAX_LENGTH),
                            hashes.SHA3_256())


def check_signature(public_key, signature, username, date_time):
    try:
        public_key.verify(signature,
                          signature_message(
                              username=username, date_time=date_time),
                          padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                      salt_length=padding.PSS.MAX_LENGTH),
                          hashes.SHA3_256())
        return True
    except InvalidSignature:
        return False
