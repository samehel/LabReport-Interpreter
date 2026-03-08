"""
Authentication service. Handles registration, login, and JWT creation.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token


async def register_user(data: UserRegister, db: AsyncSession) -> User:
    """
    Register a new user account.

    Args:
        data: Registration data (name, email, password, optional dob).
        db: Database session.

    Returns:
        Created User object.

    Raises:
        HTTPException 400 if email already exists.
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    # Create user
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        date_of_birth=data.date_of_birth
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


async def authenticate_user(data: UserLogin, db: AsyncSession) -> dict:
    """
    Authenticate a user and return a JWT token.

    Args:
        data: Login credentials (email, password).
        db: Database session.

    Returns:
        Dict with access_token and token_type.

    Raises:
        HTTPException 401 if credentials are invalid.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
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
    Change user's password.

    Args:
        user: Current authenticated user.
        current_password: The user's current password.
        new_password: The new password to set.
        db: Database session.

    Returns:
        True if password was changed.

    Raises:
        HTTPException 400 if current password is wrong.
    """
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect."
        )

    user.hashed_password = hash_password(new_password)
    await db.flush()
    return True


async def delete_account(user: User, db: AsyncSession) -> bool:
    """
    Delete a user account and all associated data.

    Args:
        user: The user to delete.
        db: Database session.

    Returns:
        True if account was deleted.
    """
    await db.delete(user)
    await db.flush()
    return True
