from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from .service import ServerServices
from .dao import InMemoryDAO


class RegisterInfo(BaseModel):
    username: str
    public_key: str
    time: str


class AuthInfo(BaseModel):
    username: str
    time: str
    signature: str


class SendMessageInfo(BaseModel):
    auth: AuthInfo
    recipient: str
    message: str


dao = InMemoryDAO()
service = ServerServices(dao)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello world!"}


@app.put("/v1/user/register", status_code=204)
async def register_user(register_info: RegisterInfo, response: Response):
    created = service.register_user(username=register_info.username,
                                    public_key=register_info.public_key, time=register_info.time)
    if created:
        return
    else:
        response.status_code = status.HTTP_409_CONFLICT
        return {"status": "There is already a user with that username"}


@app.get("/v1/user/{username}")
async def get_user_info(username: str, response: Response):
    user_info = service.get_user_info(username)
    if len(user_info['username']) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
    return service.get_user_info(username)


@app.put("/v1/user/{username}/message/send", status_code=204)
async def send_message_to_user(username: str, send_message_info: SendMessageInfo, response: Response):
    if username == send_message_info.auth.username and service.authenticate_user(send_message_info.auth):
        service.send_message_to_user(
            send_message_info.recipient, send_message_info.message)
        return
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status": "Invalid auth"}


@app.post("/v1/user/{username}/message/pull")
async def read_messages(username: str, auth: AuthInfo, response: Response):
    if username == auth.username and service.authenticate_user(auth):
        return {"messages": service.read_messages(username)}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status": "Invalid auth"}
