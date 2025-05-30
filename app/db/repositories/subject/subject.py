from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.subject import Subject
from app.schemas.subject.subject import SubjectCreate, SubjectUpdate, SubjectList
from app.db.base import BaseRepository


class SubjectRepository(BaseRepository[Subject, SubjectCreate, SubjectUpdate]):
    async def get_all(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100, 
        search: str = None, 
        order_by: str = "created_at", 
        order_direction: str = "desc",
        is_active: bool = True
    ) -> List[SubjectList]:
        query = select(Subject)
        if is_active:
            query = query.where(Subject.is_active == is_active)
        if search:
            query = query.where(Subject.name.ilike(f"%{search}%"))
        query = query.order_by(
            getattr(Subject, order_by).desc() if order_direction == "desc" 
            else getattr(Subject, order_by).asc()
        )
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        subjects = result.scalars().all()
        return [SubjectList.model_validate(subject) for subject in subjects]
    
    async def create(self, db: AsyncSession, subject: SubjectCreate) -> SubjectList:
        subject_obj = Subject(**subject.model_dump())
        db.add(subject_obj)
        await db.commit()
        await db.refresh(subject_obj)
        return SubjectList.model_validate(subject_obj)
    
    async def delete(self, db: AsyncSession, id: int) -> None:
        subject = await self.get(db=db, id=id)
        if not subject:
            raise ValueError("Subject not found")
        await db.delete(subject)
        await db.commit()
        return None


subject_repository = SubjectRepository(Subject)