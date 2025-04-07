from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from cassandra.cluster import Session
from ..auth.models import User
from ..auth.security import get_current_user
from .database import get_message_db
from .schemas import MessageCreate, MessageResponse
from .services import create_message, get_messages_between_users
import asyncio


router = APIRouter(prefix="/messages", tags=["messages"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected via WebSocket.")
        await self.broadcast_status(user_id, "online")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected from WebSocket.")
            asyncio.create_task(self.broadcast_status(user_id, "offline"))

    async def send_message(self, message: dict, recipient_id: str):
        if recipient_id in self.active_connections:
            await self.active_connections[recipient_id].send_json(message)

    async def broadcast_status(self, user_id: str, status: str):
        message = {"type": "status", "user_id": user_id, "status": status}
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_message_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.user_id
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "message")

            if message_type == "message":
                message_data = MessageCreate(**data)
                message_response = await create_message(user_id, message_data.dict(), db)
                await manager.send_message(
                    {"type": "message", "message": message_response},
                    message_data.recipient_id
                )
                await websocket.send_json({"type": "message", "status": "Message sent", "message": message_response})

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)
        await websocket.close(code=1011, reason="Internal error")

@router.get("/history/{recipient_id}", response_model=list[MessageResponse])
async def get_message_history(
    recipient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_message_db)
):
    messages = await get_messages_between_users(current_user.user_id, recipient_id, db)
    return messages

@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_message_db)
):
    message_response = await create_message(current_user.user_id, message_data.dict(), db)
    await manager.send_message(
        {"type": "message", "message": message_response},
        message_data.recipient_id
    )
    return message_response