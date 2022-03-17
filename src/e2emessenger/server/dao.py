from abc import ABC, abstractmethod


class ServerDAO(ABC):
    @abstractmethod
    def create_user(self, username, public_key):
        pass

    @abstractmethod
    def get_user_info(self, username):
        pass

    @abstractmethod
    def get_user_pending_messages(self, username):
        pass

    @abstractmethod
    def clear_user_pending_messages(self, username):
        pass

    @abstractmethod
    def save_user_message(self, sender, recipient, signature, contents):
        pass


class InMemoryDAO(ServerDAO):
    public_key_name = "public_key"
    username_name = "username"

    messages_name = "messages"
    message_sender_name = "sender"
    message_recipient_name = "recipient"
    message_signature_name = "signature"
    message_contents_name = "contents"

    def __init__(self):
        self.users = {}

    def create_user(self, username, public_key):
        if username in self.users:
            return False
        else:
            self.users[username] = {
                self.username_name: username,
                self.public_key_name: public_key,
                self.messages_name: [],
            }
            return True

    def get_user_info(self, username):
        if username in self.users:
            return {
                self.username_name: username,
                self.public_key_name: self.users[username][self.public_key_name],
            }
        else:
            return {
                self.username_name: "",
                self.public_key_name: "",
            }

    def get_user_pending_messages(self, username):
        if username in self.users:
            return self.users[username][self.messages_name]
        else:
            return []

    def clear_user_pending_messages(self, username):
        if username in self.users:
            self.users[username][self.messages_name] = []

    def save_user_message(self, sender, recipient, signature, contents):
        message = {
            self.message_sender_name: sender,
            self.message_recipient_name: recipient,
            self.message_signature_name: signature,
            self.message_contents_name: contents,
        }

        if recipient in self.users:
            self.users[recipient][self.messages_name].append(message)
