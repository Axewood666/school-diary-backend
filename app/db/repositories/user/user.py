from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import UserRole
from app.db.base import BaseRepository
from app.db.models.user import User
from app.schemas.user.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_user_admin(self, db: AsyncSession, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id, User.role == UserRole.ADMIN)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_users(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None, 
        order_by: str = "created_at", 
        order_direction: str = "desc", 
        is_active: Optional[bool] = None, 
        role: Optional[UserRole] = None
    ) -> List[User]:
        query = select(User)
        
        if role:
            query = query.where(User.role == role)
        if search:
            query = query.where(User.full_name.ilike(f"%{search}%"))
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        if order_by == "created_at":
            if order_direction == "desc":
                query = query.order_by(User.created_at.desc())
            else:
                query = query.order_by(User.created_at.asc())
        elif order_by == "id":
            if order_direction == "desc":
                query = query.order_by(User.id.desc())
            else:
                query = query.order_by(User.id.asc())
        elif order_by == "full_name":
            if order_direction == "desc":
                query = query.order_by(User.full_name.desc())
            else:
                query = query.order_by(User.full_name.asc())
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def deactivate_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        user = await self.get(db=db, id=user_id)
        if not user:
            return None 
        user.is_active = False
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


user_repository = UserRepository(User) 
