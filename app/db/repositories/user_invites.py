from app.schemas.auth import UserInviteCreate, UserInviteUpdate
from app.db.models.user import UserInvite
from app.db.base import BaseRepository
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

class UserInviteRepository(BaseRepository[UserInvite, UserInviteCreate, UserInviteUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[UserInvite]:
        query = select(UserInvite).where(UserInvite.email == email)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_token(self, db: AsyncSession, *, token: str) -> Optional[UserInvite]:
        query = select(UserInvite).where(UserInvite.token == token)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def create_user_invite(self, db: AsyncSession, *, obj_in: UserInviteCreate):
        token = str(uuid.uuid4())
        db_obj = UserInvite(
            email=obj_in.email,
            full_name=obj_in.full_name,
            role=obj_in.role,
            token=token,
            expires_at=obj_in.expires_at,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_sent_status(self, db: AsyncSession, *, user_invite_id: int):
        query = update(UserInvite).where(UserInvite.id == user_invite_id).values(is_sent=True)
        await db.execute(query)
        await db.commit()

user_invite_repository = UserInviteRepository(UserInvite)