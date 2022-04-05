import time
import unittest
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from ..crypto import crypto


class TestCryptoMethods(unittest.TestCase):
    def test_generate_key(self):
        self.assertIsInstance(crypto.generate_keypair(), rsa.RSAPrivateKey)

    def test_generate_key_multiple_different(self):
        self.assertNotEqual(crypto.generate_keypair(),
                            crypto.generate_keypair())

    def test_export_keypair(self):
        private_key = crypto.generate_keypair()
        keypair_contents = crypto.export_keypair(private_key)
        self.assertIsInstance(keypair_contents, str)
        self.assertTrue(keypair_contents.startswith(
            '-----BEGIN RSA PRIVATE KEY-----'))
        self.assertTrue(keypair_contents.endswith(
            '-----END RSA PRIVATE KEY-----\n'))

    def test_import_keypair(self):
        private_key = crypto.generate_keypair()
        original_keypair_contents = crypto.export_keypair(
            private_key=private_key)
        new_private_key = crypto.import_keypair(
            keypair_contents=original_keypair_contents)
        self.assertIsInstance(new_private_key, rsa.RSAPrivateKey)
        self.assertEqual(crypto.export_keypair(
            new_private_key), original_keypair_contents)

    def test_export_public_key(self):
        private_key = crypto.generate_keypair()
        public_key_contents = crypto.export_public_key(
            public_key=private_key.public_key())
        self.assertIsInstance(public_key_contents, str)
        self.assertTrue(public_key_contents.startswith(
            '-----BEGIN PUBLIC KEY-----'))
        self.assertTrue(public_key_contents.endswith(
            '-----END PUBLIC KEY-----\n'))

    def test_import_public_key(self):
        private_key = crypto.generate_keypair()
        original_public_key_contents = crypto.export_public_key(
            public_key=private_key.public_key())
        new_public_key = crypto.import_public_key(
            public_key_contents=original_public_key_contents)
        self.assertIsInstance(new_public_key, rsa.RSAPublicKey)
        self.assertEqual(crypto.export_public_key(
            new_public_key), original_public_key_contents)

    def test_current_date_time(self):
        first_date_time = crypto.current_date_time()
        time.sleep(.1)
        second_date_time = crypto.current_date_time()
        self.assertIsInstance(first_date_time, datetime)
        self.assertIsInstance(second_date_time, datetime)
        self.assertGreater(second_date_time, first_date_time)

    def test_generate_and_check_signature(self):
        username = 'Joshua'
        date_time = crypto.current_date_time()
        private_key = crypto.generate_keypair()
        s = crypto.generate_signature(
            private_key=private_key, username=username, date_time=date_time)
        self.assertIsInstance(s, str)
        self.assertGreater(len(s), 0)
        self.assertTrue(crypto.check_signature(public_key=private_key.public_key(),
                                               signature=s,
                                               username=username,
                                               date_time=date_time))
        different_username = 'Josh'
        self.assertFalse(crypto.check_signature(public_key=private_key.public_key(),
                                                signature=s,
                                                username=different_username,
                                                date_time=date_time))
        different_date_time = crypto.current_date_time()
        self.assertFalse(crypto.check_signature(public_key=private_key.public_key(),
                                                signature=s,
                                                username=username,
                                                date_time=different_date_time))
        different_private_key = crypto.generate_keypair()
        self.assertFalse(crypto.check_signature(public_key=different_private_key.public_key(),
                                                signature=s,
                                                username=username,
                                                date_time=date_time))

    def test_encrypt_and_decrypt(self):
        sender_private_key = crypto.generate_keypair()
        receiver_private_key = crypto.generate_keypair()
        sender = 'Joshua'
        receiver = 'Vince'
        time = crypto.current_date_time()
        message = 'Hello world!'
        ciphertext = crypto.encrypt_message(
            sender_private_key, receiver_private_key.public_key(), sender, receiver, time, message)
        self.assertIsInstance(ciphertext, str)
        self.assertGreater(len(ciphertext), 0)
        self.assertNotEqual(message, ciphertext)
        decrypted = crypto.decrypt_message(
            receiver_private_key, sender_private_key.public_key(), ciphertext)
        print(decrypted)
        self.assertIsInstance(decrypted, dict)
        self.assertEqual(sender, decrypted["sender"])
        self.assertEqual(receiver, decrypted["receiver"])
        self.assertEqual(time, decrypted["time"])
        self.assertEqual(message, decrypted["message"])
        self.assertGreater(len(decrypted["hash"]), 0)
        self.assertGreater(len(decrypted["signature"]), 0)
        different_sender_private_key = crypto.generate_keypair()
        different_sender_private_key_decrypted = crypto.decrypt_message(
            receiver_private_key, different_sender_private_key.public_key(), ciphertext)
        self.assertIsInstance(different_sender_private_key_decrypted, dict)
        self.assertEqual(
            len(different_sender_private_key_decrypted["sender"]), 0)
        self.assertEqual(
            len(different_sender_private_key_decrypted["receiver"]), 0)
        self.assertEqual(
            len(different_sender_private_key_decrypted["time"]), 0)
        self.assertEqual(
            len(different_sender_private_key_decrypted["message"]), 0)
        self.assertEqual(
            len(different_sender_private_key_decrypted["hash"]), 0)
        self.assertEqual(
            len(different_sender_private_key_decrypted["signature"]), 0)
