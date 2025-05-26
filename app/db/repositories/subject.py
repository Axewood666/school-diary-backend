from app.db.models.subject import Subject, TeacherSubject
from app.db.models.user import Teacher, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import BaseRepository
from typing import List, Optional
from sqlalchemy import select
from app.schemas.subject import SubjectCreate, SubjectUpdate, TeacherSubjectCreate, TeacherSubjectUpdate
from sqlalchemy.orm import selectinload

class SubjectRepository(BaseRepository[Subject, SubjectCreate, SubjectUpdate]):
    async def get_subjects(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
                          search: Optional[str] = None, order_by: str = "created_at", 
                          order_direction: str = "desc") -> List[Subject]:
        query = select(Subject)

        if search:
            query = query.where(Subject.name.ilike(f"%{search}%"))
        
        order_column = getattr(Subject, order_by, Subject.created_at)
        if order_direction == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_subjects_with_teachers(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
                                       search: Optional[str] = None) -> List[Subject]:
        query = select(Subject).options(
            selectinload(Subject.teacher_subjects).selectinload(TeacherSubject.teacher).selectinload(Teacher.user)
        )

        if search:
            query = query.where(Subject.name.ilike(f"%{search}%"))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_teacher_subjects(self, db: AsyncSession, teacher_id: int) -> List[Subject]:
        query = select(Subject).join(TeacherSubject).where(TeacherSubject.teacher_id == teacher_id)
        result = await db.execute(query)
        return result.scalars().all()

class TeacherSubjectRepository(BaseRepository[TeacherSubject, TeacherSubjectCreate, TeacherSubjectUpdate]):
    async def get_by_teacher_and_subject(self, db: AsyncSession, teacher_id: int, subject_id: int) -> Optional[TeacherSubject]:
        query = select(TeacherSubject).where(
            TeacherSubject.teacher_id == teacher_id,
            TeacherSubject.subject_id == subject_id
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_teacher_subjects(self, db: AsyncSession, teacher_id: int) -> List[TeacherSubject]:
        query = select(TeacherSubject).options(
            selectinload(TeacherSubject.subject)
        ).where(TeacherSubject.teacher_id == teacher_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_subject_teachers(self, db: AsyncSession, subject_id: int) -> List[TeacherSubject]:
        query = select(TeacherSubject).options(
            selectinload(TeacherSubject.teacher).selectinload(Teacher.user)
        ).where(TeacherSubject.subject_id == subject_id)
        result = await db.execute(query)
        return result.scalars().all()

subject_repository = SubjectRepository(Subject)
teacher_subject_repository = TeacherSubjectRepository(TeacherSubject) 