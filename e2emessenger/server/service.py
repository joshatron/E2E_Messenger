
class ServerServices():
    def __init__(self, dao):
        self.dao = dao

    def register_user(self, username, public_key):
        return True

    def get_user_info(self, username):
        return {"username": "", "public_key": ""}

    def send_message_to_user(self, sender, recipient, date_time, signature, message):
        return True

    def read_messages(self, username, date_time, signature):
        return []
