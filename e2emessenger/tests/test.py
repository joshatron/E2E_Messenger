import unittest
from ..crypto import keys
from cryptography.hazmat.primitives.asymmetric import rsa


class TestCryptoMethods(unittest.TestCase):
    def test_generate_key(self):
        self.assertIsInstance(keys.generate_keypair(), rsa.RSAPrivateKey)

    def test_generate_key_multiple_different(self):
        self.assertNotEqual(keys.generate_keypair(), keys.generate_keypair())


if __name__ == '__main__':
    unittest.main()
