from dao import FileBasedClientDAO
from ..crypto import keys
from ..crypto import signature
from ..crypto import message
import requests

dao = FileBasedClientDAO("client_data")
server_url = "http://localhost:8080"

(u, k) = dao.load_user_data()

username = ""
keypair = None

if len(u) == 0:
    username = "Joshua"
    keypair = keys.generate_keypair()
    r = requests.put(server_url + "/v1/user/register", data={
                     "username": username, "public_key": keys.export_public_key(keypair.public_key())})
else:
    username = u
    keypair = keys.import_keypair(k)
