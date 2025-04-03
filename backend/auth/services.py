# backend/auth/services.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User
from .security import get_password_hash
from fastapi import HTTPException  # Add this import
from sqlalchemy import or_

async def create_user(user_data: dict, db: AsyncSession) -> User:
    # Combine email and username checks into a single query
    result = await db.execute(
        select(User).filter(
            or_(
                User.email == user_data["email"],
                User.username == user_data["username"]
            )
        )
    )
    existing_user = result.scalars().first()
    if existing_user:
        if existing_user.email == user_data["email"]:
            raise HTTPException(status_code=400, detail="A user with this email already exists.")
        if existing_user.username == user_data["username"]:
            raise HTTPException(status_code=400, detail="A user with this username already exists.")

    hashed_password = get_password_hash(user_data["password"])
    new_user = User(
        username=user_data["username"],
        email=user_data["email"],
        password_hash=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user