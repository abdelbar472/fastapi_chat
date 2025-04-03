# backend/main.py
from fastapi import FastAPI
from .auth.routers import router as auth_router
from .auth.database import engine, Base

app = FastAPI()

# Create SQLite tables for auth
async def init_auth_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await init_auth_db()

app.include_router(auth_router)