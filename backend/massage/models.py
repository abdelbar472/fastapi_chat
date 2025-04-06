from cassandra.cluster import Session

def init_message_db(session: Session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id uuid PRIMARY KEY,
            sender_id uuid,
            recipient_id uuid,
            content text,
            timestamp timestamp
        )
    """)
    session.execute("CREATE INDEX IF NOT EXISTS ON messages (sender_id)")
    session.execute("CREATE INDEX IF NOT EXISTS ON messages (recipient_id)")