import requests
from .dao import FileBasedClientDAO
from ..crypto import crypto

dao = FileBasedClientDAO("client_data")
server_url = "http://e2e.joshatron.io:8000"


def try_register(proposed_username, pub_key):
    r = requests.put(server_url + "/v1/user/register", json={
                     "username": proposed_username,
                     "public_key": crypto.export_public_key(pub_key),
                     "time": crypto.current_date_time().isoformat()})
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


def send_message(to, message_contents):
    current_date_time = crypto.current_date_time()
    auth = {
        "username": username,
        "time": current_date_time.isoformat(),
        "signature": crypto.generate_signature(private_key=keypair, username=username, date_time=current_date_time)
    }
    encrypted_message = crypto.encrypt_message(peers[to], message_contents)

    r = requests.put(server_url + "/v1/user/" + username + "/message/send", json={
        "auth": auth,
        "recipient": to,
        "message": encrypted_message
    })
    if r.status_code == 204:
        print("Message sent!")
    else:
        print("Oops, something went wrong sending that message.")


def pull_messages():
    current_date_time = crypto.current_date_time()
    auth = {
        "username": username,
        "time": current_date_time.isoformat(),
        "signature": crypto.generate_signature(private_key=keypair, username=username, date_time=current_date_time)
    }
    r = requests.post(server_url + "/v1/user/" + username +
                      "/message/pull", json=auth)
    if r.status_code == 200:
        return r.json()["messages"]
    else:
        print("Oops, something went wrong pulling your messages.")
        return []


def initialize():
    (u, k) = dao.load_user_data()

    if len(u) == 0:
        print("Looks like you don't have an account set up, let's get you registered!")
        k = crypto.generate_keypair()
        while True:
            proposed_username = input("What username do you want? ").strip()
            if try_register(proposed_username=proposed_username, pub_key=k.public_key()):
                u = proposed_username
                print("Username not taken, welcome " + u + "!")
                dao.save_user_data(username=u,
                                   keypair_contents=crypto.export_keypair(k))
                break
            else:
                print(
                    "That username appears to be taken. You will need to pick a different one.")
    else:
        k = crypto.import_keypair(k)
        print("Welcome back " + u + "!")

    return (u, k)


print("######################################")
print("### End-to-End Encrypted Messenger ###")
print("######################################")
print()

(username, keypair) = initialize()
peers = dao.load_peers()
conversations = {}

while True:
    action = input(
        "What would you like to do? [find-user, pull-messages, list-peers, view-conversation, send-message, exit]: ").strip().lower()

    if action == "find" or action == "find-user":
        search = input("What user do you want to search for? ").strip()
        public_key_contents = find_user_public_key(to_search=search)
        if len(public_key_contents) == 0:
            print("That user does not appear to exist.")
        else:
            print("User found! Saving their public key for future use.")
            peers[search] = crypto.import_public_key(public_key_contents)
            dao.save_peers(peers)
    elif action == "pull" or action == "pull-messages":
        messages = pull_messages()
        if len(messages) > 0:
            print("Here are the messages you have received since your last pull:")
            for encrypted_message in messages:
                decrypted_message = crypto.decrypt(keypair, encrypted_message)
                if len(decrypted_message["from"]) == 0:
                    print("Illegal message found, ignoring")
                else:
                    conversation_contents = {
                        "sent": False, "time": decrypted_message["time"], "message": decrypted_message["message"]}
                    if decrypted_message["from"] in conversations:
                        conversations[decrypted_message["from"]].append(
                            conversation_contents)
                    else:
                        conversations[decrypted_message["from"]] = [
                            conversation_contents]
        else:
            print("Looks like there is nothing new.")
        print()
    elif action == "list" or action == "list-peers":
        print("Here are your current list of peers:")
        for peer in peers:
            print("\t" + peer)
        print()
    elif action == "view" or action == "view-conversation":
        other = input("Which conversation do you want to view? ")
        if other in conversations:
            for message in conversations[other]:
                if message["sent"]:
                    print("OUT " + message["time"] + ": " + message["message"])
                else:
                    print("IN " + message["time"] + ": " + message["message"])
        else:
            print("You don't appear to have any conversations with that user.")
    elif action == "send" or action == "send-message":
        to = input("Who would you like to send a message to? ")
        if to not in peers:
            print("You need to pick someone who is already a peer.")
        else:
            to_send = input("What would you like to say? ")
            send_message(to, to_send)
            conversation_contents = {
                "sent": True, "time": decrypted_message["time"], "message": decrypted_message["message"]}
            if to_send in conversations:
                conversations[to_send].append(conversation_contents)
            else:
                conversations[to_send] = [conversation_contents]
    elif action == "exit":
        print("Have a good day.")
        break
    else:
        print(
            "Action not recognized. Please choose from [find-user/find, pull-messages/pull, list-peers/list, view-conversation/view, send-message/send, exit].")
