from .dao import FileBasedClientDAO
from .service import ClientServices

dao = FileBasedClientDAO("client_data")
service = ClientServices(dao)

print("######################################")
print("### End-to-End Encrypted Messenger ###")
print("######################################")
print()

while True:
    action = input(
        "What would you like to do? [find-user, pull-messages, list-peers, view-conversation, send-message, exit]: ").strip().lower()

    if action == "find" or action == "find-user":
        service.find_user()
    elif action == "pull" or action == "pull-messages":
        service.pull_messages()
    elif action == "list" or action == "list-peers":
        service.list_peers()
    elif action == "view" or action == "view-conversation":
        service.view_conversation()
    elif action == "send" or action == "send-message":
        service.send_message()
    elif action == "exit":
        print("Have a good day.")
        break
    else:
        print(
            "Action not recognized. Please choose from [find-user/find, pull-messages/pull, list-peers/list, view-conversation/view, send-message/send, exit].")
