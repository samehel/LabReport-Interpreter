from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional


class UserRegister(BaseModel):
    """Schema for user registration."""
    name: str
    email: EmailStr
    password: str
    date_of_birth: Optional[date] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    name: str
    email: str
    date_of_birth: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters")
        return v
