from cassandra.cluster import Session
from cassandra.query import SimpleStatement
import uuid
from datetime import datetime

async def create_message(
    sender_id: str,
    message_data: dict,
    db: Session
) -> dict:
    message_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()

    query = SimpleStatement("""
        INSERT INTO messages (message_id, sender_id, recipient_id, content, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """)
    db.execute(query, (
        uuid.UUID(message_id),
        uuid.UUID(sender_id),
        uuid.UUID(message_data["recipient_id"]),
        message_data["content"],
        timestamp
    ))

    return {
        "message_id": message_id,
        "sender_id": sender_id,
        "recipient_id": message_data["recipient_id"],
        "content": message_data["content"],
        "timestamp": timestamp.isoformat()
    }

async def get_messages_between_users(
    user_id: str,
    recipient_id: str,
    db: Session
) -> list:
    query = SimpleStatement("""
        SELECT message_id, sender_id, recipient_id, content, timestamp
        FROM messages
        WHERE (sender_id = %s AND recipient_id = %s)
           OR (sender_id = %s AND recipient_id = %s)
    """)
    rows = db.execute(query, (
        uuid.UUID(user_id),
        uuid.UUID(recipient_id),
        uuid.UUID(recipient_id),
        uuid.UUID(user_id)
    ))

    messages = []
    for row in rows:
        messages.append({
            "message_id": str(row.message_id),
            "sender_id": str(row.sender_id),
            "recipient_id": str(row.recipient_id),
            "content": row.content,
            "timestamp": row.timestamp.isoformat()
        })
    return messages