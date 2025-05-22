from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.schemas.role import UserRole
from app.db.base import BaseRepository
from app.db.models.user import User, UserInvite, Student, Teacher
from app.schemas.role import StudentInDb, TeacherInDb, UserBase, UserCreate, UserUpdate, UserStudent, UserTeacher
from typing import List
from sqlalchemy.orm import selectinload
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
    
    async def create_student(self, db: AsyncSession, student_in: StudentInDb):
        db_add = Student(**student_in.model_dump())
        db.add(db_add)
        await db.commit()
        await db.refresh(db_add)
        return db_add
    async def create_teacher(self, db: AsyncSession, teacher_in: TeacherInDb):
        db_add = Teacher(**teacher_in.model_dump())
        db.add(db_add)
        await db.commit()
        await db.refresh(db_add)
        return db_add
    async def get_user_student(self, db: AsyncSession, user_id: int) -> UserStudent:
        query = select(Student).where(Student.user_id == user_id).options(selectinload(Student.user))
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_user_teacher(self, db: AsyncSession, user_id: int) -> UserTeacher:
        query = select(Teacher).where(Teacher.user_id == user_id).options(selectinload(Teacher.user))
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_user_admin(self, db: AsyncSession, user_id: int) -> User:
        query = select(User).where(User.id == user_id, User.role == UserRole.ADMIN)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_all_students(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[UserStudent]:
        query = select(Student).options(selectinload(Student.user)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_teachers(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[UserTeacher]:
        query = select(Teacher).options(selectinload(Teacher.user)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_admins(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        query = select(User).where(User.role == UserRole.ADMIN).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def deactivate_user(self, db: AsyncSession, user_id: int) -> User:
        user = await self.get(db=db, id=user_id)
        if not user:
            return None 
        user.is_active = False
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

user_repository = UserRepository(User) 
