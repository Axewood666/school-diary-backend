from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.repositories.user import user_repository
from app.schemas.auth import Token, UserCreate


async def get_user_by_id(db: AsyncSession, user_id: int):
    return await user_repository.get(db=db, id=user_id)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await user_repository.get_by_username(db=db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(db: AsyncSession, user_in: UserCreate):
    existing_user = await user_repository.get_by_email(db=db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    existing_username = await user_repository.get_by_username(db=db, username=user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.dict(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    
    db_user = await user_repository.create(db=db, obj_in=UserCreate(**user_data))
    return db_user


def create_user_token(user_id: str) -> Token:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer") 