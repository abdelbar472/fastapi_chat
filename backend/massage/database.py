from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from decouple import config

DATABASE_HOST = config("MESSAGE_DATABASE_HOST", default="localhost")
DATABASE_PORT = config("MESSAGE_DATABASE_PORT", cast=int, default=9042)
DATABASE_KEYSPACE = config("MESSAGE_DATABASE_KEYSPACE", default="chat_app")

cluster = Cluster([DATABASE_HOST], port=DATABASE_PORT)
session = cluster.connect(DATABASE_KEYSPACE)

def get_message_db():
    try:
        yield session
    finally:
        pass

def shutdown_db():
    cluster.shutdown()