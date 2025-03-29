from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class MessageCreate(BaseModel):
    sender: str
    receiver: str
    content: str

class MessageResponse(BaseModel):
    id: UUID
    sender: str
    receiver: str
    content: str
    timestamp: datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str