from fastapi import APIRouter

from app.schemas.subject import Subject, SubjectList
from app.schemas.base import BaseResponse, ErrorResponse
from app.db.repositories.subject import subject_repository
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from fastapi import Depends

import logging
from app.utils.logging import setup_logging

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["subject"])

@router.get("/", response_model=Union[BaseResponse[List[Subject]], ErrorResponse])
async def get_subjects(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        subjects = await subject_repository.get_all(db=db)
        return success_response(data=subjects, message="Subjects retrieved successfully")
    except Exception as e:
        logger.error(f"GET_SUBJECTS_ERROR: {e}")
        return error_response(message="Failed to get subjects", error_code="GET_SUBJECTS_ERROR")