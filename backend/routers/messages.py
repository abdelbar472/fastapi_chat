from fastapi import APIRouter
from  backend.schemas import MessageCreate, MessageResponse
from  backend.services import save_message, get_chat_history

router = APIRouter()

@router.post("/messages/", response_model=MessageResponse)
def send_message(message: MessageCreate):
    return save_message(message.sender, message.receiver, message.content)

@router.get("/messages/{user1}/{user2}", response_model=list[MessageResponse])
def chat_history(user1: str, user2: str):
    return get_chat_history(user1, user2)
