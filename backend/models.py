from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    id: UUID
    sender: str
    receiver: str
    content: str
    timestamp: datetime
class User(BaseModel):
    id: UUID
    username: str
    email: str
    hashed_password: str