import base64
import json
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
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


def __generate_hash_value_for_message(sender, receiver, time, message):
    return sender + " " + receiver + " " + time.isoformat() + " " + message


def __hash_string(str):
    hash = hashes.Hash(hashes.SHA256())
    hash.update(str.encode('utf-8'))
    return base64.b64encode(hash.finalize()).decode('utf-8')


def __sign_hashed(hash, private_key):
    decoded_hash = base64.b64decode(hash)
    signature = private_key.sign(
        decoded_hash, __signature_padding(), utils.Prehashed(__signature_hash()))
    return base64.b64encode(signature).decode('utf-8')


def __verify_signed_hashed(hash, signature, public_key):
    try:
        decoded_hash = base64.b64decode(hash)
        decoded_signature = base64.b64decode(signature)
        public_key.verify(decoded_signature,
                          decoded_hash,
                          __signature_padding(),
                          utils.Prehashed(__signature_hash()))
        return True
    except InvalidSignature:
        return False


def encrypt_message(sender_private_key, receiver_public_key, sender, receiver, time, message):
    hash_contents = __hash_string(
        __generate_hash_value_for_message(sender, receiver, time, message))
    contents = json.dumps({"from": sender, "to": receiver, "time": time.isoformat(
    ), "message": message, "hash": hash_contents, "signature": __sign_hashed(hash_contents, sender_private_key)})
    split_contents = [contents[i:i+100] for i in range(0, len(contents), 100)]
    final_encrypted = ""
    for part in split_contents:
        encrypted = base64.b64encode(receiver_public_key.encrypt(
            part.encode('utf-8'), __message_padding())).decode('utf-8')
        final_encrypted += encrypted
        if part != split_contents[len(split_contents)-1]:
            final_encrypted += '|'
    return final_encrypted


def decrypt_message(receiver_private_key, peer_public_keys, ciphertext):
    parts = ciphertext.split('|')
    final_decrypted_message = ""
    for part in parts:
        decoded_ciphertext = base64.b64decode(part)
        decrypted_part = receiver_private_key.decrypt(
            decoded_ciphertext, __message_padding()).decode('utf-8')
        final_decrypted_message += decrypted_part
    decrypted_object = json.loads(final_decrypted_message)
    calculated_hash = __hash_string(
        __generate_hash_value_for_message(decrypted_object["from"], decrypted_object["to"], datetime.fromisoformat(decrypted_object["time"]), decrypted_object["message"]))

    if decrypted_object['from'] in peer_public_keys and calculated_hash == decrypted_object["hash"] and __verify_signed_hashed(decrypted_object["hash"], decrypted_object["signature"], peer_public_keys[decrypted_object["from"]]):
        return decrypted_object
    else:
        return {"to": "", "from": "", "time": "", "message": "", "hash": "", "signature": ""}
