from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import BaseRepository
from app.db.models.user import User, Teacher
from app.db.models.schedule import Schedule
from app.schemas.teacher import TeacherInDb, UserTeacher, TeacherUpdate


class TeacherRepository(BaseRepository[Teacher, TeacherInDb, TeacherUpdate]):
    async def create_teacher(self, db: AsyncSession, teacher_in: TeacherInDb) -> Teacher:
        db_add = Teacher(**teacher_in.model_dump())
        db.add(db_add)
        await db.commit()
        await db.refresh(db_add)
        return db_add

    async def get_user_teacher(self, db: AsyncSession, user_id: int) -> Optional[UserTeacher]:
        query = select(Teacher).where(Teacher.user_id == user_id).options(selectinload(Teacher.user))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_teachers(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None, 
        order_by: str = "created_at", 
        order_direction: str = "desc",
        is_active: Optional[bool] = None,
        class_id: Optional[int] = None
    ) -> List[UserTeacher]:
        query = select(Teacher).options(selectinload(Teacher.user))
        
        if search:
            query = query.where(Teacher.user.has(User.full_name.ilike(f"%{search}%")))
            
        if class_id is not None:
            if class_id == 0:
                class_id = None
            query = query.where(Teacher.class_id == class_id)
            
        if is_active is not None:
            query = query.where(Teacher.user.has(User.is_active == is_active))
            
        if order_by == "created_at":
            query = query.join(Teacher.user).order_by(
                User.created_at.desc() if order_direction == "desc" 
                else User.created_at.asc()
            )
        elif order_by == "class_id":
            query = query.order_by(
                Teacher.class_id.desc() if order_direction == "desc" 
                else Teacher.class_id.asc()
            )
        elif order_by == "id" or order_by == "user_id":
            query = query.order_by(
                Teacher.user_id.desc() if order_direction == "desc" 
                else Teacher.user_id.asc()
            )
        elif order_by == "full_name":
            query = query.join(Teacher.user).order_by(
                User.full_name.desc() if order_direction == "desc" 
                else User.full_name.asc()
            )

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def is_class_teacher(self, db: AsyncSession, user_id: int, class_id: int) -> bool:
        query = select(Schedule).where(
            Schedule.teacher_id == user_id,
            Schedule.class_id == class_id
        )
        result = await db.execute(query)
        return result.first() is not None


teacher_repository = TeacherRepository(Teacher) 