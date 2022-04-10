import base64
import json
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature


DETAILED_OUTPUT = True

# Keys


def generate_keypair():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def export_keypair(private_key, password):
    return private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                     format=serialization.PrivateFormat.TraditionalOpenSSL,
                                     encryption_algorithm=serialization.BestAvailableEncryption(password.encode('utf-8'))).decode('utf-8')


def import_keypair(keypair_contents, password):
    try:
        return serialization.load_pem_private_key(keypair_contents.encode('utf-8'), password=password.encode('utf-8'))
    except Exception:
        return None


def export_public_key(public_key):
    return public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                   format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')


def import_public_key(public_key_contents):
    return serialization.load_pem_public_key(public_key_contents.encode('utf-8'))


# Signatures

def current_date_time():
    return datetime.now()


def generate_auth_signature(private_key, username, date_time):
    return __sign_hashed(__hash_string(__generate_auth_string_to_sign(username, date_time)), private_key)


def __sign_hashed(encoded_hash, private_key):
    decoded_hash = base64.b64decode(encoded_hash)
    signature = private_key.sign(
        decoded_hash, __get_signature_padding(), utils.Prehashed(__get_hash_algorithm()))
    return base64.b64encode(signature).decode('utf-8')


def verify_auth_signature(public_key, signature, username, date_time):
    return __verify_signed_hash(__hash_string(
        __generate_auth_string_to_sign(username, date_time)), signature, public_key)


def __verify_signed_hash(encoded_hash, signature, public_key):
    try:
        decoded_hash = base64.b64decode(encoded_hash)
        decoded_signature = base64.b64decode(signature)
        public_key.verify(decoded_signature,
                          decoded_hash,
                          __get_signature_padding(),
                          utils.Prehashed(__get_hash_algorithm()))
        return True
    except InvalidSignature:
        return False


def __generate_auth_string_to_sign(username, date_time):
    return (username + " " + date_time.isoformat())


def __hash_string(string_to_hash):
    digest = hashes.Hash(__get_hash_algorithm())
    digest.update(string_to_hash.encode('utf-8'))
    return base64.b64encode(digest.finalize()).decode('utf-8')


def __get_signature_padding():
    return padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                       salt_length=padding.PSS.MAX_LENGTH)


def __get_hash_algorithm():
    return hashes.SHA256()

# Messages


def encrypt_message(sender_private_key, receiver_public_key, sender, receiver, time, message):
    hash_contents = __hash_string(
        __generate_message_string_to_sign(sender, receiver, time, message))
    signature_contents = __sign_hashed(hash_contents, sender_private_key)
    final_contents = __generate_final_message_string(
        sender, receiver, time, message, hash_contents, signature_contents)
    if DETAILED_OUTPUT:
        print("Encrypting message with following contents: " + final_contents)
    ciphertext = __encrypt_long_message(receiver_public_key, final_contents)
    if DETAILED_OUTPUT:
        print("Sending encrypted message: " + ciphertext)
    return ciphertext


def __generate_final_message_string(sender, receiver, time, message, encoded_hash, encoded_signature):
    return json.dumps({"from": sender, "to": receiver, "time": time.isoformat(), "message": message, "hash": encoded_hash, "signature": encoded_signature})


def __encrypt_long_message(public_key, message):
    split_contents = __split_long_message(message)
    final_encrypted = ""
    for part in split_contents:
        encrypted = public_key.encrypt(
            part.encode('utf-8'), __get_message_padding())
        encoded_encrypted = base64.b64encode(encrypted).decode('utf-8')
        final_encrypted += encoded_encrypted
        if not __is_last_element(part, split_contents):
            final_encrypted += __get_message_separator()
    return final_encrypted


def __split_long_message(message):
    return [message[i:i+100] for i in range(0, len(message), 100)]


def __is_last_element(element, list_to_check):
    return element == list_to_check[len(list_to_check)-1]


def decrypt_message(receiver_private_key, peer_public_keys, ciphertext):
    if DETAILED_OUTPUT:
        print("Received encrypted message: " + ciphertext)
    decrypted_message = __decrypt_long_message(
        receiver_private_key, ciphertext)
    decrypted_object = json.loads(decrypted_message)
    if DETAILED_OUTPUT:
        print("Decrypted message into: " + decrypted_message)

    if decrypted_object["from"] not in peer_public_keys:
        return {"to": "", "from": decrypted_object["from"], "time": "", "message": "", "hash": "", "signature": ""}

    if __verify_decrypted_message(decrypted_object, peer_public_keys):
        return decrypted_object
    else:
        return {"to": "", "from": "", "time": "", "message": "", "hash": "", "signature": ""}


def __decrypt_long_message(private_key, message):
    parts = __split_encrypted_into_parts(message)
    final_decrypted_message = ""
    for part in parts:
        decoded_ciphertext = base64.b64decode(part)
        decrypted_part = private_key.decrypt(
            decoded_ciphertext, __get_message_padding()).decode('utf-8')
        final_decrypted_message += decrypted_part
    return final_decrypted_message


def __split_encrypted_into_parts(encrypted_message):
    return encrypted_message.split(__get_message_separator())


def __verify_decrypted_message(decrypted_object, peer_public_keys):
    if DETAILED_OUTPUT:
        print("Verifying integrity of message.")
    calculated_hash = __hash_string(
        __generate_message_string_to_sign(decrypted_object["from"], decrypted_object["to"], datetime.fromisoformat(decrypted_object["time"]), decrypted_object["message"]))

    if decrypted_object["from"] not in peer_public_keys:
        print("Peer public key not found.")
        return False

    if DETAILED_OUTPUT:
        print("Given hash:      " + decrypted_object["hash"])
        print("Calculated hash: " + calculated_hash)

    if calculated_hash != decrypted_object["hash"]:
        return False

    if __verify_signed_hash(decrypted_object["hash"], decrypted_object["signature"], peer_public_keys[decrypted_object["from"]]):
        if DETAILED_OUTPUT:
            print("Verified signature '" +
                  decrypted_object["signature"] + "' is from " + decrypted_object["from"] + " for these message contents")
        return True
    else:
        return False


def __get_message_separator():
    return "|"


def __generate_message_string_to_sign(sender, receiver, time, message):
    return sender + " " + receiver + " " + time.isoformat() + " " + message


def __get_message_padding():
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
