from  backend.db import db_session
from  backend.models import Message, User
from uuid import uuid4
import datetime
from security import hash_password, verify_password, create_access_token



def save_message(sender: str, receiver: str, content: str):
    message_id = uuid4()
    timestamp = datetime.datetime.utcnow()

    query = """
    INSERT INTO messages (id, sender, receiver, content, timestamp) 
    VALUES (%s, %s, %s, %s, %s)
    """
    db_session.execute(query, (message_id, sender, receiver, content, timestamp))

    return Message(id=message_id, sender=sender, receiver=receiver, content=content, timestamp=timestamp)


def get_chat_history(user1: str, user2: str):
    query = """
    SELECT id, sender, receiver, content, timestamp FROM messages
    WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s)
    """
    rows = db_session.execute(query, (user1, user2, user2, user1))

    return [Message(id=row.id, sender=row.sender, receiver=row.receiver, content=row.content, timestamp=row.timestamp)
            for row in rows]


def register_user(username: str, email: str, password: str):
    user_id = uuid4()
    hashed_password = hash_password(password)

    query = """
    INSERT INTO users (id, username, email, hashed_password)
    VALUES (%s, %s, %s, %s)
    """
    db_session.execute(query, (user_id, username, email, hashed_password))

    return {"id": user_id, "username": username, "email": email}


def authenticate_user(username: str, password: str):
    query = "SELECT id, username, email, hashed_password FROM users WHERE username = %s"
    rows = db_session.execute(query, (username,))

    user = rows.one()
    if not user or not verify_password(password, user.hashed_password):
        return None

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}