import time
import unittest
from ..crypto import keys
from ..crypto import message
from ..crypto import signature
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime


class TestCryptoMethods(unittest.TestCase):
    def test_generate_key(self):
        self.assertIsInstance(keys.generate_keypair(), rsa.RSAPrivateKey)

    def test_generate_key_multiple_different(self):
        self.assertNotEqual(keys.generate_keypair(), keys.generate_keypair())

    def test_export_keypair(self):
        private_key = keys.generate_keypair()
        keypair_contents = keys.export_keypair(private_key)
        self.assertIsInstance(keypair_contents, str)
        self.assertTrue(keypair_contents.startswith(
            '-----BEGIN RSA PRIVATE KEY-----'))
        self.assertTrue(keypair_contents.endswith(
            '-----END RSA PRIVATE KEY-----\n'))

    def test_import_keypair(self):
        private_key = keys.generate_keypair()
        original_keypair_contents = keys.export_keypair(
            private_key=private_key)
        new_private_key = keys.import_keypair(
            keypair_contents=original_keypair_contents)
        self.assertIsInstance(new_private_key, rsa.RSAPrivateKey)
        self.assertEqual(keys.export_keypair(
            new_private_key), original_keypair_contents)

    def test_export_public_key(self):
        private_key = keys.generate_keypair()
        public_key_contents = keys.export_public_key(
            public_key=private_key.public_key())
        self.assertIsInstance(public_key_contents, str)
        self.assertTrue(public_key_contents.startswith(
            '-----BEGIN PUBLIC KEY-----'))
        self.assertTrue(public_key_contents.endswith(
            '-----END PUBLIC KEY-----\n'))

    def test_import_public_key(self):
        private_key = keys.generate_keypair()
        original_public_key_contents = keys.export_public_key(
            public_key=private_key.public_key())
        new_public_key = keys.import_public_key(
            public_key_contents=original_public_key_contents)
        self.assertIsInstance(new_public_key, rsa.RSAPublicKey)
        self.assertEqual(keys.export_public_key(
            new_public_key), original_public_key_contents)

    def test_current_date_time(self):
        first_date_time = signature.current_date_time()
        time.sleep(.1)
        second_date_time = signature.current_date_time()
        self.assertIsInstance(first_date_time, datetime)
        self.assertIsInstance(second_date_time, datetime)
        self.assertGreater(second_date_time, first_date_time)

    def test_generate_and_check_signature(self):
        username = 'Joshua'
        date_time = signature.current_date_time()
        private_key = keys.generate_keypair()
        s = signature.generate_signature(
            private_key=private_key, username=username, date_time=date_time)
        self.assertIsInstance(s, str)
        self.assertGreater(len(s), 0)
        self.assertTrue(signature.check_signature(public_key=private_key.public_key(),
                                                  signature=s,
                                                  username=username,
                                                  date_time=date_time))
        different_username = 'Josh'
        self.assertFalse(signature.check_signature(public_key=private_key.public_key(),
                                                   signature=s,
                                                   username=different_username,
                                                   date_time=date_time))
        different_date_time = signature.current_date_time()
        self.assertFalse(signature.check_signature(public_key=private_key.public_key(),
                                                   signature=s,
                                                   username=username,
                                                   date_time=different_date_time))
        different_private_key = keys.generate_keypair()
        self.assertFalse(signature.check_signature(public_key=different_private_key.public_key(),
                                                   signature=s,
                                                   username=username,
                                                   date_time=date_time))

    def test_encrypt_and_decrypt(self):
        private_key = keys.generate_keypair()
        m = 'Hello world!'
        ciphertext = message.encrypt(
            public_key=private_key.public_key(), message=m)
        self.assertIsInstance(ciphertext, str)
        self.assertGreater(len(ciphertext), 0)
        self.assertNotEqual(m, ciphertext)
        decrypted = message.decrypt(
            private_key=private_key, ciphertext=ciphertext)
        self.assertIsInstance(decrypted, str)
        self.assertGreater(len(decrypted), 0)
        self.assertEqual(m, decrypted)
