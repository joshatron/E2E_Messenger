import unittest
from ..crypto import keys
from cryptography.hazmat.primitives.asymmetric import rsa


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
