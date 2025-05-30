from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import BaseRepository
from app.db.models.user import User, Student
from app.db.models.schedule import Schedule
from app.schemas.user.student import StudentInDb, UserStudent, StudentUpdate


class StudentRepository(BaseRepository[Student, StudentInDb, StudentUpdate]):
    async def create_student(self, db: AsyncSession, student_in: StudentInDb) -> Student:
        db_add = Student(**student_in.model_dump())
        db.add(db_add)
        await db.commit()
        await db.refresh(db_add)
        return db_add

    async def get_user_student(self, db: AsyncSession, user_id: int) -> Optional[UserStudent]:
        query = select(Student).where(Student.user_id == user_id).options(selectinload(Student.user))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_students(
        self, 
        db: AsyncSession, 
        teacher_id: Optional[int] = None,
        class_id: Optional[int] = None,
        search: Optional[str] = None,
        order_by: str = "created_at",
        order_direction: str = "desc",
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[UserStudent]:
        query = select(Student).options(selectinload(Student.user))
        
        if teacher_id:
            query = query.where(
                or_(
                    Student.class_id.in_(
                        select(Schedule.class_id).where(
                            Schedule.teacher_id == teacher_id
                        ).distinct()
                    )
                )
            )
    
        if class_id is not None:
            if class_id == 0:
                class_id = None
            query = query.where(Student.class_id == class_id)
        
        if search:
            query = query.where(
                or_(
                    Student.user.has(User.full_name.ilike(f"%{search}%")),
                    Student.user.has(User.email.ilike(f"%{search}%"))
                )
            )
        
        if is_active is not None:
            query = query.where(Student.user.has(User.is_active == is_active))
        
        if order_by == "created_at":
            query = query.join(Student.user).order_by(
                User.created_at.desc() if order_direction == "desc" 
                else User.created_at.asc()
            )
        elif order_by == "class_id":
            query = query.order_by(
                Student.class_id.desc() if order_direction == "desc" 
                else Student.class_id.asc()
            )
        elif order_by == "id" or order_by == "user_id":
            query = query.order_by(
                Student.user_id.desc() if order_direction == "desc" 
                else Student.user_id.asc()
            )
        elif order_by == "full_name":
            query = query.join(Student.user).order_by(
                User.full_name.desc() if order_direction == "desc" 
                else User.full_name.asc()
            )
                
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


student_repository = StudentRepository(Student) 