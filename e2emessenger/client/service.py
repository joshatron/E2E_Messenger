import requests
from ..crypto import crypto


class ClientServices():
    def __init__(self, dao):
        self.dao = dao
        (self.server_url, self.username, self.keypair) = self.initialize()
        self.peers = self.dao.load_peers()
        self.conversations = self.dao.load_conversations()

    def initialize(self):
        (server_url, username, keypair) = self.dao.load_user_data()

        if len(username) == 0:
            print(
                "Looks like you don't have an account set up, let's get you registered!")
            keypair = crypto.generate_keypair()
            server_url = self.__query_server_url()
            username = self.__query_username(server_url, keypair)
        else:
            keypair = crypto.import_keypair(keypair)
            print("Welcome back " + username + "!")

        return (server_url, username, keypair)

    def __query_server_url(self):
        while True:
            proposed_server_url = input(
                "Where is the server you want to connect to? ").strip()
            if self.__try_ping(proposed_server_url):
                print("Server found!")
                return proposed_server_url
            else:
                print("That server address doesn't appear to be correct.")

    def __try_ping(self, proposed_server_url):
        try:
            r = requests.get(proposed_server_url + "/v1/health")
            return r.status_code == 200
        except Exception:
            return False

    def __query_username(self, server_url, keypair):
        while True:
            proposed_username = input("What username do you want? ").strip()
            if self.__try_register(server_url, proposed_username, keypair.public_key()):
                print("Username not taken, welcome " + proposed_username + "!")
                self.dao.save_user_data(
                    server_url, proposed_username, crypto.export_keypair(keypair))
                return proposed_username
            else:
                print(
                    "That username appears to be taken. You will need to pick a different one.")

    def __try_register(self, server_url, proposed_username, pub_key):
        r = requests.put(server_url + "/v1/user/register", json={
            "username": proposed_username,
            "public_key": crypto.export_public_key(pub_key),
            "time": crypto.current_date_time().isoformat()})
        if r.status_code == 204:
            return True
        else:
            return False

    def find_user(self):
        search = input("What user do you want to search for? ").strip()
        public_key_contents = self.__find_user_public_key(search)
        if len(public_key_contents) == 0:
            print("That user does not appear to exist.")
        else:
            print("User found! Saving their public key for future use.")
            print()
            self.peers[search] = crypto.import_public_key(public_key_contents)
            self.dao.save_peers(self.peers)

    def __find_user_public_key(self, to_search):
        r = requests.get(self.server_url + "/v1/user/" + to_search)
        if r.status_code == 200:
            return r.json()['public_key']
        else:
            return ""

    def list_peers(self):
        print("Here are your current list of peers:")
        for peer in self.peers:
            print("\t" + peer)
        print()

    def pull_messages(self):
        messages = self.__pull_messages_from_server()
        if len(messages) > 0:
            for encrypted_message in messages:
                decrypted_message = crypto.decrypt_message(
                    self.keypair, self.peers, encrypted_message)
                if len(decrypted_message["from"]) == 0:
                    print("Illegal message found, ignoring")
                else:
                    conversation_contents = {
                        "sent": False, "time": decrypted_message["time"], "message": decrypted_message["message"]}
                    if decrypted_message["from"] in self.conversations:
                        self.conversations[decrypted_message["from"]].append(
                            conversation_contents)
                    else:
                        self.conversations[decrypted_message["from"]] = [
                            conversation_contents]
                    print("Pulled down message from " +
                          decrypted_message["from"])
            self.dao.save_conversations(self.conversations)
        else:
            print("Looks like there is nothing new.")
        print()

    def __pull_messages_from_server(self):
        auth = self.__generate_auth_object()
        r = requests.post(self.server_url + "/v1/user/" +
                          self.username + "/message/pull", json=auth)
        if r.status_code == 200:
            return r.json()["messages"]
        else:
            print("Oops, something went wrong pulling your messages.")
            return []

    def __generate_auth_object(self):
        current_date_time = crypto.current_date_time()
        return {
            "username": self.username,
            "time": current_date_time.isoformat(),
            "signature": crypto.generate_auth_signature(private_key=self.keypair, username=self.username, date_time=current_date_time)
        }

    def view_conversation(self):
        other = input("Which conversation do you want to view? ")
        if other in self.conversations:
            for message in self.conversations[other]:
                self.__print_conversation_message(
                    message["sent"], message["time"], message["message"])
            print()
        else:
            print("You don't appear to have any conversations with that user.")

    def __print_conversation_message(self, sent, time, message):
        if sent:
            full_time = (" " * (100-len(time))) + time
            print(full_time)
            for line in self.__split_message_into_lines(message):
                full_line = (" " * (100-len(line))) + line
                print(full_line)
        else:
            print(time)
            for line in self.__split_message_into_lines(message):
                print(line)
        print()

    def __split_message_into_lines(self, message):
        return [message[i:i+60] for i in range(0, len(message), 60)]

    def send_message(self):
        recipient = input("Who would you like to send a message to? ")
        if recipient not in self.peers:
            print("You need to pick someone who is already a peer.")
        else:
            to_send = input("What would you like to say? ")
            self.__send_message_to_server(recipient, to_send)
            conversation_contents = {
                "sent": True, "time": crypto.current_date_time().isoformat(), "message": to_send}
            if recipient in self.conversations:
                self.conversations[recipient].append(conversation_contents)
            else:
                self.conversations[recipient] = [conversation_contents]
            self.dao.save_conversations(self.conversations)
            print()

    def __send_message_to_server(self, recipient, message_contents):
        auth = self.__generate_auth_object()
        encrypted_message = crypto.encrypt_message(
            self.keypair, self.peers[recipient], self.username, recipient, crypto.current_date_time(), message_contents)

        r = requests.put(self.server_url + "/v1/user/" + self.username + "/message/send", json={
            "auth": auth,
            "recipient": recipient,
            "message": encrypted_message
        })
        if r.status_code == 204:
            print("Message sent!")
        else:
            print("Oops, something went wrong sending that message.")
