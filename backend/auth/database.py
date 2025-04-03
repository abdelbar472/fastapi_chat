# backend/auth/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from decouple import config

DATABASE_URL = config("AUTH_DATABASE_URL", default="sqlite+aiosqlite:///auth.db")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_auth_db():
    async with SessionLocal() as session:
        yield session