# backend/auth/models.py
from sqlalchemy import Column, String, Boolean, DateTime, LargeBinary, Index
from sqlalchemy.sql import func
from .database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_joined = Column(DateTime, default=func.now())
    profile_image = Column(LargeBinary, nullable=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)  # Added missing field

    __table_args__ = (
        Index('ix_users_email', 'email'),
        Index('ix_users_username', 'username'),
    )
