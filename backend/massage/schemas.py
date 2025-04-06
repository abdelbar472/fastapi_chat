from pydantic import BaseModel

class MessageCreate(BaseModel):
    recipient_id: str
    content: str

class MessageResponse(BaseModel):
    message_id: str
    sender_id: str
    recipient_id: str
    content: str
    timestamp: str

    class Config:
        from_attributes = True