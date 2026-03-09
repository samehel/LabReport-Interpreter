"""
Auth router. Handles registration, OTP verification, login, profile, and account management.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister, UserLogin, Token, UserResponse,
    PasswordChange, OTPVerify, OTPResend,
)
from app.services.auth_service import (
    register_user, authenticate_user, change_password,
    delete_account, verify_otp, resend_otp,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.
    An OTP verification code is sent to the provided email.
    The account must be verified before login is allowed.
    """
    user = await register_user(data, db)
    return user


@router.post("/verify-otp")
async def verify(data: OTPVerify, db: AsyncSession = Depends(get_db)):
    """
    Verify email with the OTP code sent during registration.
    On success, returns a JWT token (auto-login) and sends a welcome email.
    """
    return await verify_otp(data.email, data.otp_code, db)


@router.post("/resend-otp")
async def resend(data: OTPResend, db: AsyncSession = Depends(get_db)):
    """
    Request a new OTP code. Use this if the original OTP expired
    or the email was not received.
    """
    return await resend_otp(data.email, db)


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password.
    Returns a JWT access token valid for 24 hours.
    Only verified accounts can log in.
    """
    return await authenticate_user(data, db)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.put("/password")
async def update_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change the current user's password. A confirmation email is sent."""
    await change_password(current_user, data.current_password, data.new_password, db)
    return {"message": "Password updated successfully."}


@router.delete("/account")
async def remove_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete the current user's account and all associated data. A farewell email is sent."""
    await delete_account(current_user, db)
    return {"message": "Account deleted successfully."}
