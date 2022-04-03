from operator import truediv
from .dao import FileBasedClientDAO
from ..crypto import keys
from ..crypto import signature
from ..crypto import message
import requests

dao = FileBasedClientDAO("client_data")
server_url = "http://localhost:8000"


def try_register(proposed_username, pub_key):
    r = requests.put(server_url + "/v1/user/register", json={
                     "username": proposed_username,
                     "public_key": keys.export_public_key(pub_key),
                     "time": signature.current_date_time().isoformat()})
    if r.status_code == 204:
        return True
    else:
        return False


print("######################################")
print("### End-to-End Encrypted Messenger ###")
print("######################################")
print()

(u, k) = dao.load_user_data()

username = ""
keypair = None

if len(u) == 0:
    print("Looks like you don't have an account set up, let's get you registered!")
    keypair = keys.generate_keypair()
    while True:
        proposed_username = input("What username do you want? ").strip()
        if try_register(proposed_username=proposed_username, pub_key=keypair.public_key()):
            username = proposed_username
            print("Username not taken, welcome " + username + "!")
            dao.save_user_data(username=username,
                               keypair_contents=keys.export_keypair(keypair))
            break
        else:
            print(
                "That username appears to be taken. You will need to pick a different one.")
else:
    username = u
    keypair = keys.import_keypair(k)
    print("Welcome back " + username + "!")
