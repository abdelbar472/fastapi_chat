from cassandra.cluster import Cluster

def get_db():
    cluster = Cluster(["127.0.0.1"])  # Update if remote
    session = cluster.connect()
    session.set_keyspace("chat_app")
    return session

db_session = get_db()
