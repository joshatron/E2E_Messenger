import os
from abc import ABC, abstractmethod


class ClientDAO(ABC):
    @abstractmethod
    def save_user_data(self, username, keypair_contents):
        pass

    @abstractmethod
    def load_user_data(self):
        pass


class FileBasedClientDAO(ClientDAO):
    KEY_FILE_NAME = "key.private"
    USERNAME_FILE_NAME = "username.txt"

    def __init__(self, base_dir):
        self.base_dir = base_dir
        try:
            os.mkdir(self.base_dir)
        except FileExistsError:
            pass

    def save_user_data(self, username, keypair_contents):
        with open(os.path.join(self.base_dir, self.USERNAME_FILE_NAME), "w+", encoding="utf-8") as username_file:
            username_file.write(username)
        with open(os.path.join(self.base_dir, self.KEY_FILE_NAME), "w+", encoding="utf-8") as key_file:
            key_file.write(keypair_contents)

    def load_user_data(self):
        username = ""
        keypair_contents = ""
        try:
            with open(os.path.join(self.base_dir, self.USERNAME_FILE_NAME), "r", encoding="utf-8") as username_file:
                username = username_file.read()
            with open(os.path.join(self.base_dir, self.KEY_FILE_NAME), "r", encoding="utf-8") as key_file:
                keypair_contents = key_file.read()
            return (username, keypair_contents)
        except IOError:
            return ('', '')
