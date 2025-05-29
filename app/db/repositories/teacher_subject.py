from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.base import BaseRepository
from app.db.models.subject import Subject, TeacherSubject
from app.db.models.user import Teacher
from app.schemas.subject import TeacherSubjectCreate, TeacherSubjectUpdate


class TeacherSubjectRepository(BaseRepository[TeacherSubject, TeacherSubjectCreate, TeacherSubjectUpdate]):
    async def add_teacher_subject(self, db: AsyncSession, subject_id: int, teacher_id: int) -> TeacherSubject:
        teacher_subject = TeacherSubject(subject_id=subject_id, teacher_id=teacher_id)
        db.add(teacher_subject)
        await db.commit()
        await db.refresh(teacher_subject)
        return teacher_subject
    
    async def remove_teacher_subject(self, db: AsyncSession, subject_id: int, teacher_id: int) -> None:
        teacher_subject = await self.get_teacher_subject(db=db, subject_id=subject_id, teacher_id=teacher_id)
        if not teacher_subject:
            raise ValueError("Teacher subject not found")
        await db.delete(teacher_subject)
        await db.commit()
        return None
    
    async def get_teacher_subject(self, db: AsyncSession, subject_id: int, teacher_id: int) -> Optional[TeacherSubject]:
        query = select(TeacherSubject).where(
            TeacherSubject.subject_id == subject_id,
            TeacherSubject.teacher_id == teacher_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_teachers_by_subject(
        self, 
        db: AsyncSession, 
        subject_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[TeacherSubject]:
        query = select(TeacherSubject).where(
            TeacherSubject.subject_id == subject_id
        ).options(
            joinedload(TeacherSubject.teacher).joinedload(Teacher.user)
        )
        query = query.order_by(TeacherSubject.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        teacher_subjects = result.scalars().all()
        return teacher_subjects
    
    async def get_subjects_by_teacher(self, db: AsyncSession, teacher_id: int) -> List[Subject]:
        query = select(Subject).join(TeacherSubject).where(
            TeacherSubject.teacher_id == teacher_id
        ).options(
            joinedload(Subject.teacher_subjects).joinedload(TeacherSubject.subject)
        )
        result = await db.execute(query)
        subjects = result.unique().scalars().all()
        return subjects


teacher_subject_repository = TeacherSubjectRepository(TeacherSubject) 