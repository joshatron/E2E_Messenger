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


def find_user_public_key(to_search):
    r = requests.get(server_url + "/v1/user/" + to_search)
    if r.status_code == 200:
        return r.json()['public_key']
    else:
        return ""


def initialize():
    (u, k) = dao.load_user_data()

    if len(u) == 0:
        print("Looks like you don't have an account set up, let's get you registered!")
        k = keys.generate_keypair()
        while True:
            proposed_username = input("What username do you want? ").strip()
            if try_register(proposed_username=proposed_username, pub_key=k.public_key()):
                u = proposed_username
                print("Username not taken, welcome " + u + "!")
                dao.save_user_data(username=u,
                                   keypair_contents=keys.export_keypair(k))
                break
            else:
                print(
                    "That username appears to be taken. You will need to pick a different one.")
    else:
        k = keys.import_keypair(k)
        print("Welcome back " + u + "!")

    return (u, k)


print("######################################")
print("### End-to-End Encrypted Messenger ###")
print("######################################")
print()

(username, keypair) = initialize()
peers = dao.load_peers()

while True:
    action = input(
        "What would you like to do? [find-user, pull-messages, list-users, view-conversation, send-message, exit]: ").strip().lower()

    if action == "find" or action == "find-user":
        search = input("What user do you want to search for? ").strip()
        public_key_contents = find_user_public_key(to_search=search)
        if len(public_key_contents) == 0:
            print("That user does not appear to exist.")
        else:
            print("User found! Saving their public key for future use.")
            peers[search] = public_key_contents
            dao.save_peers(peers)
    elif action == "exit":
        print("Have a good day.")
        break
    else:
        print(
            "Action not recognized. Please choose from [find-user/find, pull-messages/pull, list-users/list, view-conversation/view, send-message/send, exit].")
