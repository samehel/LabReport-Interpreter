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


class OTPVerify(BaseModel):
    """Schema for OTP verification after registration."""
    email: EmailStr
    otp_code: str

    @field_validator("otp_code")
    @classmethod
    def otp_format(cls, v: str) -> str:
        if not v.strip().isdigit() or len(v.strip()) != 6:
            raise ValueError("OTP must be a 6-digit code")
        return v.strip()


class OTPResend(BaseModel):
    """Schema for requesting a new OTP code."""
    email: EmailStr


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
    is_verified: bool = False
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
