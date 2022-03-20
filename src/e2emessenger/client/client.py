from ..crypto import keys

private_key = keys.generate_keypair()
keys.save_keypair(private_key=private_key, loc='client_data')
new_private_key = keys.load_keypair(loc='client_data')
