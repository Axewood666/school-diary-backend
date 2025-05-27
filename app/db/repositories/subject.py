from app.db.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectList
from app.db.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.models.subject import TeacherSubject
from app.db.models.user import Teacher
from sqlalchemy.orm import joinedload
from app.schemas.teacher import UserWithTeacherInfo

class SubjectRepository(BaseRepository[Subject, SubjectCreate, SubjectUpdate]):
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
                        search: str = None, 
                        order_by: str = "created_at", order_direction: str = "desc",
                        is_active: bool = True) -> List[SubjectList]:
        query = select(Subject)
        if is_active:
            query = query.where(Subject.is_active == is_active)
        if search:
            query = query.where(Subject.name.ilike(f"%{search}%"))
        query = query.order_by(getattr(Subject, order_by).desc() if order_direction == "desc" else getattr(Subject, order_by).asc())
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        subjects = result.scalars().all()
        return [SubjectList.model_validate(subject) for subject in subjects]
    
    async def create(self, db: AsyncSession, subject: SubjectCreate) -> SubjectList:
        subject = Subject(**subject.model_dump())
        db.add(subject)
        await db.commit()
        await db.refresh(subject)
        return SubjectList.model_validate(subject)
    
    async def delete(self, db: AsyncSession, id: int) -> None:
        subject = await self.get(db=db, id=id)
        if not subject:
            raise ValueError("Subject not found")
        await db.delete(subject)
        await db.commit()
        return None
    
    async def add_teacher_subject(self, db: AsyncSession, subject_id: int, teacher_id: int) -> TeacherSubject:
        teacher_subject = TeacherSubject(subject_id=subject_id, teacher_id=teacher_id)
        db.add(teacher_subject)
        await db.commit()
        await db.refresh(teacher_subject)
        return teacher_subject
    
    async def remove_teacher_subject(self, db: AsyncSession, subject_id: int, teacher_id: int) -> None:
        teacher_subject = await self.get_teacher_subjects(db=db, subject_id=subject_id, teacher_id=teacher_id)
        if not teacher_subject:
            raise ValueError("Teacher subject not found")
        await db.delete(teacher_subject)
        await db.commit()
        return None
    
    async def get_teacher_subject(self, db: AsyncSession, subject_id: int, teacher_id: int) -> TeacherSubject:
        query = select(TeacherSubject).where(
            TeacherSubject.subject_id == subject_id,
            TeacherSubject.teacher_id == teacher_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_teachers_by_subject(self,db: AsyncSession, subject_id: int, 
                                    skip: int = 0, limit: int = 100) -> List[TeacherSubject]:
        query = select(TeacherSubject).where(
            TeacherSubject.subject_id == subject_id).options(
                joinedload(TeacherSubject.teacher).joinedload(Teacher.user))
        query = query.order_by(TeacherSubject.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        teacher_subjects = result.scalars().all()
        return teacher_subjects
    
    async def get_subjects_by_teacher(self, db: AsyncSession, teacher_id: int) -> List[Subject]:
        query = select(Subject).join(TeacherSubject).where(
            TeacherSubject.teacher_id == teacher_id).options(
                joinedload(Subject.teacher_subjects).joinedload(TeacherSubject.subject))
        result = await db.execute(query)
        subjects = result.unique().scalars().all()
        return subjects
    
subject_repository = SubjectRepository(Subject)