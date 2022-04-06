import os
from abc import ABC, abstractmethod
from ..crypto import crypto


class ClientDAO(ABC):
    @abstractmethod
    def save_user_data(self, username, keypair_contents):
        pass

    @abstractmethod
    def load_user_data(self):
        pass

    @abstractmethod
    def save_peers(self, peers):
        pass

    @abstractmethod
    def load_peers(self):
        pass


class FileBasedClientDAO(ClientDAO):
    KEY_FILE_NAME = "key.private"
    USERNAME_FILE_NAME = "username.txt"
    PEER_KEY_FOLDER_NAME = "peers"

    def __init__(self, base_dir):
        self.base_dir = base_dir
        try:
            os.mkdir(self.base_dir)
            os.mkdir(os.path.join(self.base_dir, self.PEER_KEY_FOLDER_NAME))
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

    def save_peers(self, peers):
        for peer in peers:
            with open(os.path.join(self.base_dir, self.PEER_KEY_FOLDER_NAME, peer), "w+", encoding="utf-8") as peer_file:
                peer_file.write(crypto.export_public_key(peers[peer]))

    def load_peers(self):
        peers = {}

        for peer in os.listdir(os.path.join(self.base_dir, self.PEER_KEY_FOLDER_NAME)):
            with open(os.path.join(self.base_dir, self.PEER_KEY_FOLDER_NAME, peer), "r", encoding="utf-8") as peer_file:
                peers[peer] = crypto.import_public_key(peer_file.read())

        return peers
