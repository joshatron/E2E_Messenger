from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from .service import ServerServices
from .dao import InMemoryDAO


class RegisterInfo(BaseModel):
    username: str
    public_key: str
    time: str


class SendMessageInfo(BaseModel):
    username: str
    date_time: str
    signature: str
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


@app.put("/v1/user/{username}/message/send")
async def send_message_to_user(username: str, send_message_info: SendMessageInfo):
    return {"status": service.send_message_to_user(sender=send_message_info.username,
                                                   recipient=username,
                                                   date_time=send_message_info.date_time,
                                                   signature=send_message_info.signature,
                                                   message=send_message_info.message)}


@app.get("/v1/user/{username}/message/read")
async def read_messages(username: str, date_time: str, signature: str):
    return service.read_messages(username=username, date_time=date_time, signature=signature)
