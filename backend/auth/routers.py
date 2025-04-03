# backend/auth/routers.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import get_auth_db
from .models import User
from .schemas import UserCreate, UserLogin, UserResponse
from .security import get_password_hash, verify_password, create_access_token, create_refresh_token, get_current_user
from .services import create_user
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from decouple import config
import os
import aiofiles
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])

conf = ConnectionConfig(
    MAIL_USERNAME=config("EMAIL_HOST_USER"),
    MAIL_PASSWORD=config("EMAIL_HOST_PASSWORD"),
    MAIL_FROM=config("EMAIL_HOST_USER"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

async def save_file(file: UploadFile) -> str:
    upload_dir = "uploads/profile"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
    return file_path

async def send_welcome_email(email: str, username: str):
    message = MessageSchema(
        subject="Welcome to the App!",
        recipients=[email],
        body=f"Hi {username},\nWelcome to the app! Your profile setup is pending.",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

@router.post("/signup")
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_auth_db), background_tasks: BackgroundTasks = None):
    user_dict = user_data.dict()
    new_user = await create_user(user_dict, db)

    # Offload email sending to a background task
    if background_tasks:
        background_tasks.add_task(send_welcome_email, new_user.email, new_user.username)

    return JSONResponse(
        content={"redirect_url": "http://127.0.0.1:8000/profile/"},
        status_code=status.HTTP_201_CREATED
    )

@router.get("/login")
async def login_get():
    return {"message": "This endpoint requires a POST request with email and password. Use /docs for interactive API documentation."}

@router.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_auth_db)):
    result = await db.execute(select(User).filter(User.email == user_data.email))
    user = result.scalars().first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account is inactive.")

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "message": "Login successful!",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "redirect_url": "http://127.0.0.1:8000/teams/"
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logout successful"}

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/profile")
async def update_profile(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    profile_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_auth_db)
):
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    if profile_image:
        file_path = await save_file(profile_image)
        current_user.profile_image = file_path

    await db.commit()
    await db.refresh(current_user)
    return {"message": "Profile updated successfully"}