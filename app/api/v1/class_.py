from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.base import error_response, BaseResponse, ErrorResponse, success_response
from app.schemas.user import UserRole, User

from app.core.dependencies import get_db
from app.core.logger import setup_logging
from app.db.models.user import User
from app.core.dependencies import get_current_user
from datetime import datetime
from app.db.repositories.class_ import class_repository
from app.schemas.class_ import ClassList
import logging
from typing import List, Union

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["class"])

@router.get("/", response_model=Union[BaseResponse[List[ClassList]], ErrorResponse])
async def get_classes(skip: int = 0, limit: int = 100, search: str = None, order_by: str = "created_at", order_direction: str = "desc", year: int = datetime.now().year, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
    
        classes = await class_repository.get_classes(db=db, search=search, order_by=order_by, order_direction=order_direction, year=year, skip=skip, limit=limit)
        
        class_list = []
        for class_ in classes:
            class_list.append(ClassList(
                id=class_.id,
                name=class_.name,
                year_id=class_.year_id,
                year_name=class_.year.name,
                created_at=class_.created_at,
            ))
        print(class_list)
        return success_response(
            data=class_list,
            message="Classes retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_CLASS_ERROR: {e}")
        return error_response(
            message="Failed to get class",
            error_code="GET_CLASS_ERROR"
        )