from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.base import BaseRepository
from app.db.models.user import User, UserInvite, Student, Teacher
from app.schemas.auth import UserCreate, UserUpdate
from app.schemas.role import StudentInDb, TeacherInDb
from typing import List

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalars().first()

    
    async def create_student(self, db: AsyncSession, student_in: StudentInDb):
        db_add = Student(**student_in)
        db.add(db_add)
        await db.commit()
        await db.refresh(db_add)
        return db_add
    async def create_teacher(self, db: AsyncSession, teacher_in: TeacherInDb):
        db_add = Teacher(**teacher_in)
        db.add(db_add)
        await db.commit()
        await db.refresh(db_add)
        return db_add
    
user_repository = UserRepository(User) 