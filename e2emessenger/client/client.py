from ..crypto import keys
from ..crypto import signature
from ..crypto import message

private_key = keys.generate_keypair()

username = 'Joshua'
date_time = signature.current_date_time()
s = signature.generate_signature(
    private_key=private_key, username=username, date_time=date_time)

print(signature.check_signature(public_key=private_key.public_key(),
      signature=s, username=username, date_time=date_time))

m = 'Hello world!'
ciphertext = message.encrypt(public_key=private_key.public_key(), message=m)
print(ciphertext)
m2 = message.decrypt(private_key=private_key, ciphertext=ciphertext)
print(m2)
