import os
import json
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


class InMemoryServerDAO(ServerDAO):
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
                self.LAST_DATE_TIME_NAME: time,
            }
            return True

    def get_user_info(self, username):
        if username in self.users:
            users = self.users[username]
            return {
                self.USERNAME_NAME: users[self.USERNAME_NAME],
                self.PUBLIC_KEY_NAME: users[self.PUBLIC_KEY_NAME],
                self.MESSAGES_NAME: users[self.MESSAGES_NAME],
                self.LAST_DATE_TIME_NAME: datetime.fromisoformat(users[self.LAST_DATE_TIME_NAME]),
            }
        else:
            return {
                self.USERNAME_NAME: "",
                self.PUBLIC_KEY_NAME: "",
                self.MESSAGES_NAME: [],
                self.LAST_DATE_TIME_NAME: datetime.min,
            }

    def update_user_auth_time(self, username, date_time):
        if username in self.users:
            self.users[username][self.LAST_DATE_TIME_NAME] = date_time.isoformat()

    def get_user_pending_messages(self, username):
        if username in self.users:
            return self.users[username][self.MESSAGES_NAME]
        else:
            return []

    def clear_user_pending_messages(self, username):
        if username in self.users:
            self.users[username][self.MESSAGES_NAME] = []

    def save_user_message(self, recipient, message):
        if recipient in self.users:
            self.users[recipient][self.MESSAGES_NAME].append(message)


class FileBasedServerDAO(ServerDAO):
    STORAGE_FOLDER = "server_data"
    STORAGE_FILE = "server_data.json"

    def __init__(self):
        self.in_memory = InMemoryServerDAO()
        try:
            os.mkdir(self.STORAGE_FOLDER)
        except FileExistsError:
            self.__load_data()
            self.__save_data()

    def __load_data(self):
        with open(os.path.join(self.STORAGE_FOLDER, self.STORAGE_FILE), "r", encoding="utf-8") as storage_file:
            self.in_memory.users = json.loads(storage_file.read())

    def __save_data(self):
        with open(os.path.join(self.STORAGE_FOLDER, self.STORAGE_FILE), "w+", encoding="utf-8") as storage_file:
            storage_file.write(json.dumps(self.in_memory.users))

    def create_user(self, username, public_key, time):
        result = self.in_memory.create_user(username, public_key, time)
        self.__save_data()
        return result

    def get_user_info(self, username):
        return self.in_memory.get_user_info(username)

    def update_user_auth_time(self, username, date_time):
        self.in_memory.update_user_auth_time(username, date_time)
        self.__save_data()

    def get_user_pending_messages(self, username):
        return self.in_memory.get_user_pending_messages(username)

    def clear_user_pending_messages(self, username):
        self.in_memory.clear_user_pending_messages(username)
        self.__save_data()

    def save_user_message(self, recipient, message):
        self.in_memory.save_user_message(recipient, message)
        self.__save_data()
