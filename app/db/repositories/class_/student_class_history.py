from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import BaseRepository
from app.db.models.class_ import StudentClassHistory, StudentClassHistoryReason
from app.schemas.class_.class_ import StudentClassHistoryCreate, StudentClassHistoryUpdate


class StudentClassHistoryRepository(BaseRepository[StudentClassHistory, StudentClassHistoryCreate, StudentClassHistoryUpdate]):
    async def write_assign(
        self, 
        db: AsyncSession, 
        student_id: int, 
        class_id: Optional[int] = None, 
        reason: StudentClassHistoryReason = StudentClassHistoryReason.ADMISSION, 
        is_active: bool = True
    ) -> StudentClassHistory:
        previous_history = await db.scalar(
            select(StudentClassHistory).where(
                StudentClassHistory.student_id == student_id, 
                StudentClassHistory.is_active == True
            )
        )
        if previous_history:
            previous_history.end_date = datetime.now()
            previous_history.is_active = False
            db.add(previous_history)
            await db.commit()
            await db.refresh(previous_history)
            
        history = StudentClassHistory()
        history.student_id = student_id
        history.class_id = class_id
        history.reason = reason
        history.is_active = is_active
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history


student_class_history_repository = StudentClassHistoryRepository(StudentClassHistory) 