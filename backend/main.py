# backend/main.py
from fastapi import FastAPI
from .auth.routers import router as auth_router
from .auth.database import engine, Base
from .massage.routers import router as message_router
from .massage.database import shutdown_db, get_message_db
from .massage.models import init_message_db

app = FastAPI()

# Create SQLite tables for auth
async def init_auth_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await init_auth_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Real-Time Chat App with ScyllaDB!"}

app.include_router(auth_router)
app.include_router(message_router)