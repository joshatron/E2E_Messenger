from datetime import datetime
from abc import ABC, abstractmethod


class ServerDAO(ABC):
    @abstractmethod
    def create_user(self, username, public_key, time):
        pass

    @abstractmethod
    def get_user_info(self, username):
        pass

    @abstractmethod
    def update_user_auth_time(self, username, date_time):
        pass

    @abstractmethod
    def get_user_pending_messages(self, username):
        pass

    @abstractmethod
    def clear_user_pending_messages(self, username):
        pass

    @abstractmethod
    def save_user_message(self, recipient, message):
        pass


class InMemoryDAO(ServerDAO):
    PUBLIC_KEY_NAME = "public_key"
    USERNAME_NAME = "username"
    LAST_DATE_TIME_NAME = "last_date_time"

    MESSAGES_NAME = "messages"

    def __init__(self):
        self.users = {}

    def create_user(self, username, public_key, time):
        if username in self.users:
            return False
        else:
            self.users[username] = {
                self.USERNAME_NAME: username,
                self.PUBLIC_KEY_NAME: public_key,
                self.MESSAGES_NAME: [],
                self.LAST_DATE_TIME_NAME: datetime.fromisoformat(time),
            }
            return True

    def get_user_info(self, username):
        if username in self.users:
            return self.users[username]
        else:
            return {
                self.USERNAME_NAME: "",
                self.PUBLIC_KEY_NAME: "",
                self.MESSAGES_NAME: [],
                self.LAST_DATE_TIME_NAME: datetime.min,
            }

    def update_user_auth_time(self, username, date_time):
        if username in self.users:
            self.users[username][self.LAST_DATE_TIME_NAME] = date_time

    def get_user_pending_messages(self, username):
        if username in self.users:
            return self.users[username][self.MESSAGES_NAME]
        else:
            return []

    def clear_user_pending_messages(self, username):
        if username in self.users:
            self.users[username][self.MESSAGES_NAME] = []
        print(self.users)

    def save_user_message(self, recipient, message):
        if recipient in self.users:
            self.users[recipient][self.MESSAGES_NAME].append(message)
        print(self.users)
