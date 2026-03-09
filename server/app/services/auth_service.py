"""
Authentication service. Handles registration, OTP verification, login, and JWT creation.
Sends emails at each key point in the auth lifecycle.
"""

import random
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.config import settings
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.email_service import send_email_background
from app.utils.email_templates import (
    otp_verification_email,
    welcome_email,
    password_changed_email,
    account_deleted_email,
)


def _generate_otp() -> str:
    """Generate a 6-digit OTP code."""
    return str(random.randint(100000, 999999))


async def register_user(data: UserRegister, db: AsyncSession) -> User:
    """
    Register a new user. Creates unverified account and sends OTP email.
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    # Generate OTP
    otp_code = _generate_otp()
    otp_expires = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    # Create unverified user
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        date_of_birth=data.date_of_birth,
        is_verified=False,
        otp_code=otp_code,
        otp_expires_at=otp_expires,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Send OTP email (fire-and-forget)
    subject, html_body = otp_verification_email(user.name, otp_code)
    send_email_background(user.email, subject, html_body)

    return user


async def verify_otp(email: str, otp_code: str, db: AsyncSession) -> dict:
    """
    Verify OTP code and activate the user account.
    On success, sends welcome email and returns a JWT token.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email."
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already verified."
        )

    # Check OTP expiry
    if user.otp_expires_at and datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )

    # Check OTP code
    if user.otp_code != otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code."
        )

    # Verify the user
    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    await db.flush()

    # Send welcome email (fire-and-forget)
    subject, html_body = welcome_email(user.name)
    send_email_background(user.email, subject, html_body)

    # Return JWT token so user is automatically logged in after verification
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Email verified successfully. Welcome!"
    }


async def resend_otp(email: str, db: AsyncSession) -> dict:
    """
    Resend a new OTP code to the user's email.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email."
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already verified."
        )

    # Generate new OTP
    otp_code = _generate_otp()
    user.otp_code = otp_code
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    await db.flush()

    # Send OTP email
    subject, html_body = otp_verification_email(user.name, otp_code)
    send_email_background(user.email, subject, html_body)

    return {"message": "A new OTP has been sent to your email."}


async def authenticate_user(data: UserLogin, db: AsyncSession) -> dict:
    """
    Authenticate a user and return a JWT token.
    Only verified users can log in.
    """
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox for the OTP code."
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


async def change_password(
    user: User,
    current_password: str,
    new_password: str,
    db: AsyncSession
) -> bool:
    """
    Change user's password. Sends confirmation email.
    """
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect."
        )

    user.hashed_password = hash_password(new_password)
    await db.flush()

    # Send password changed email
    subject, html_body = password_changed_email(user.name)
    send_email_background(user.email, subject, html_body)

    return True


async def delete_account(user: User, db: AsyncSession) -> bool:
    """
    Delete a user account. Sends farewell email before deletion.
    """
    email = user.email
    name = user.name

    await db.delete(user)
    await db.flush()

    # Send account deleted email
    subject, html_body = account_deleted_email(name)
    send_email_background(email, subject, html_body)

    return True
