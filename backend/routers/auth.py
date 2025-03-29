from fastapi import APIRouter, Depends, HTTPException, status
from  backend.schemas import UserCreate, TokenResponse
from  backend.services import register_user, authenticate_user

router = APIRouter()

@router.post("/register/")
def register(user: UserCreate):
    return register_user(user.username, user.email, user.password)

@router.post("/login/", response_model=TokenResponse)
def login(user: UserCreate):
    token = authenticate_user(user.username, user.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return token
