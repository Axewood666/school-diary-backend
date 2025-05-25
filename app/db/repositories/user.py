from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import UserRole
from app.db.base import BaseRepository
from app.db.models.user import User, Student, Teacher
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.student import StudentInDb, UserStudent
from app.schemas.teacher import TeacherInDb, UserTeacher
from app.db.models.schedule import Schedule

from typing import List
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_

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

    async def get_students(
        self, 
        db: AsyncSession, 
        teacher: Optional[Teacher] = None,
        class_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        search: Optional[str] = None,
        order_by: str = "created_at",
        order_direction: str = "desc",
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[UserStudent]:
        query = select(Student).options(selectinload(Student.user))
        
        if teacher:
            query = query.where(
                or_(
                    Student.class_id.in_(
                        select(Schedule.class_id).where(
                            Schedule.teacher_id == teacher.user_id
                        ).distinct()
                    ),
                    Student.class_id == teacher.class_id
                )
            )
    
        if class_id is not None:
            if class_id == 0:
                class_id = None
            query = query.where(Student.class_id == class_id)
            
        if teacher_id:
            query = query.where(
                Student.class_id.in_(
                    select(Schedule.class_id).where(
                        Schedule.teacher_id == teacher_id
                    ).distinct()
                )
            )
        
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
    
    async def get_teachers(self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None, order_by: str = "created_at", order_direction: str = "desc", is_active: Optional[bool] = None, class_id: Optional[int] = None) -> List[UserTeacher]:
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
    
    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None, order_by: str = "created_at", order_direction: str = "desc", is_active: Optional[bool] = None, role: Optional[UserRole] = None) -> List[User]:
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
