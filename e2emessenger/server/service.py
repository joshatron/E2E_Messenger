from datetime import datetime
from ..crypto import crypto


class ServerServices():
    def __init__(self, dao):
        self.dao = dao

    def register_user(self, username, public_key, time):
        return self.dao.create_user(username, public_key, time)

    def get_user_info(self, username):
        user_info = self.dao.get_user_info(username)
        return {"username": user_info["username"], "public_key": user_info["public_key"]}

    def authenticate_user(self, auth):
        request_time = datetime.fromisoformat(auth.time)
        user_info = self.dao.get_user_info(auth.username)
        if auth.username == user_info['username'] and request_time > user_info['last_date_time'] and crypto.check_signature(
                crypto.import_public_key(user_info['public_key']), auth.signature, auth.username, request_time):
            self.dao.update_user_auth_time(auth.username, request_time)
            return True
        else:
            return False

    def send_message_to_user(self, recipient, message):
        self.dao.save_user_message(recipient, message)

    def read_messages(self, username):
        messages = self.dao.get_user_pending_messages(username)
        self.dao.clear_user_pending_messages(username=username)
        return messages
