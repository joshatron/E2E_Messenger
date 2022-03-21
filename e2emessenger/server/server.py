from fastapi import FastAPI
from pydantic import BaseModel


class RegisterInfo(BaseModel):
    username: str
    public_key: str


class SendMessageInfo(BaseModel):
    username: str
    date_time: str
    signature: str
    message: str


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello world!"}


@app.put("/v1/user/register")
async def register_user(register_info: RegisterInfo):
    return {"status": True}


@app.get("/v1/user/{username}")
async def get_user_info(username: str):
    return {"username": "", "public_key": ""}


@app.put("/v1/user/{username}/message/send")
async def send_message_to_user(username: str, send_message_info: SendMessageInfo):
    return {"status": True}


@app.get("/v1/user/{username}/message/read")
async def read_messages(username: str, date_time: str, signature: str):
    return []
