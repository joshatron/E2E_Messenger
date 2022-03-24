from ..crypto import keys
from ..crypto import signature


class ServerServices():
    def __init__(self, dao):
        self.dao = dao

    def register_user(self, username, public_key):
        return self.dao.create_user(username, public_key)

    def get_user_info(self, username):
        user_info = self.dao.get_user_info(username)
        return {"username": user_info["username"], "public_key": user_info["public_key"]}

    def send_message_to_user(self, sender, recipient, date_time, sig, message):
        user_info = self.dao.get_user_info(sender)
        if signature.check_signature(public_key=keys.import_public_key(user_info["public_key"]), signature=sig, username=sender, date_time=date_time):
            self.dao.save_user_message(
                sender=sender, recipient=recipient, date_time=date_time, signature=sig, contents=message)
            return True
        else:
            return False

    def read_messages(self, username, date_time, sig):
        user_info = self.dao.get_user_info(username)
        if signature.check_signature(public_key=keys.import_public_key(user_info["public_key"]), signature=sig, username=username, date_time=date_time):
            messages = self.dao.get_user_pending_messages(username=username)
            self.dao.clear_user_pending_messages(username=username)
            return messages
        else:
            return []
