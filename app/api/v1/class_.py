from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.base import error_response, BaseResponse, ErrorResponse, success_response
from app.schemas.user import UserRole, User
from app.schemas.responses import UpdatedClassStudentsListData

from app.core.dependencies import get_db
from app.core.logger import setup_logging
from app.db.models.user import User
from app.core.dependencies import get_current_user
from datetime import datetime
from app.db.repositories.class_ import class_repository
from app.db.repositories.user import user_repository
from app.schemas.class_ import ClassList, ClassCreate, ClassCreateDb, ClassUpdate
import logging
from typing import List, Union
from app.db.repositories.academic_cycles import academic_cycles_repository
from app.services.class_ import add_students_to_class, remove_students_from_class

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["class"])

@router.get("/", response_model=Union[BaseResponse[List[ClassList]], ErrorResponse])
async def get_classes(skip: int = 0, limit: int = 100, search: str = None, order_by: str = "created_at", order_direction: str = "desc", year: int = datetime.now().year, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role == UserRole.TEACHER:
            teacher = await user_repository.get_user_teacher(db=db, user_id=current_user.id)
            classes = await class_repository.get_classes(db=db, teacher=teacher, search=search, order_by=order_by, order_direction=order_direction, year=year, skip=skip, limit=limit)
        elif current_user.role == UserRole.ADMIN:
            classes = await class_repository.get_classes(db=db, search=search, order_by=order_by, order_direction=order_direction, year=year, skip=skip, limit=limit)
        else:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        class_list = []
        for class_ in classes:
            class_list.append(ClassList(
                id=class_.id,
                name=class_.name,
                year_id=class_.year_id,
                year_name=class_.year.name,
                created_at=class_.created_at,
            ))

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
        
@router.post("/", response_model=Union[BaseResponse[ClassList], ErrorResponse])
async def create_class(class_create: ClassCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
            
        year = await academic_cycles_repository.get_current_academic_year(db=db)
        if not year:
            return error_response(
                message="Current academic year not found",
                error_code="CURRENT_ACADEMIC_YEAR_NOT_FOUND"
            )

        class_ = await class_repository.create(db=db, obj_in=ClassCreateDb(
            name=class_create.name,
            year_id=year.id
        ))
        
        return success_response(
            data=ClassList(
                id=class_.id,
                name=class_.name,
                year_id=class_.year_id,
                year_name=year.name,
                created_at=class_.created_at,
            ),
            message="Class created successfully"
        )
        
    except Exception as e:
        logger.error(f"CREATE_CLASS_ERROR: {e}")
        return error_response(
            message="Failed to create class",
            error_code="CREATE_CLASS_ERROR"
        )

@router.patch("/{class_id}", response_model=Union[BaseResponse[ClassList], ErrorResponse])
async def update_class(class_id: int, class_update: ClassUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
            
        class_ = await class_repository.get(db=db, id=class_id)
        if not class_:
            return error_response(
                message="Class not found",
                error_code="CLASS_NOT_FOUND"
            )
        
        class_ = await class_repository.update(db=db, db_obj=class_, obj_in=class_update)
        class_year = await academic_cycles_repository.get_academic_year_by_id(db=db, id=class_.year_id)
        
        return success_response(
            data=ClassList(
                id=class_.id,
                name=class_.name,
                year_id=class_.year_id,
                year_name=class_year.name,
                created_at=class_.created_at,
            ),
            message="Class updated successfully"
        )
    except Exception as e:
        logger.error(f"UPDATE_CLASS_ERROR: {e}")
        return error_response(
            message="Failed to update class",
            error_code="UPDATE_CLASS_ERROR"
        )
        
@router.post("/{class_id}/students", response_model=Union[BaseResponse[UpdatedClassStudentsListData], ErrorResponse])
async def update_class_students(class_id: int, new_students: List[int] = None, remove_students: List[int] = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Input:
        - new_students: List[int] - List of student ids to add to the class
        - remove_students: List[int] - List of student ids to remove from the class
    Output:
        - UpdatedClassStudentsListData - Added and removed students with their info
    """
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        if not new_students and not remove_students:
            return error_response(
                message="No students to add or remove",
                error_code="NO_STUDENTS_TO_ADD_OR_REMOVE"
            )
        
        class_ = await class_repository.get(db=db, id=class_id)
        if not class_:
            return error_response(
                message="Class not found",
                error_code="CLASS_NOT_FOUND"
            )
        students_list = []
        removed_students_list = []
        if new_students:
            students_list = await add_students_to_class(db=db, students=new_students, class_id=class_id)
        if remove_students:
            removed_students_list = await remove_students_from_class(db=db, students=remove_students, class_id=class_id)
        
        if len(students_list) == 0 and len(removed_students_list) == 0:
            return error_response(
                message="No students to add or remove",
                error_code="NO_STUDENTS_TO_ADD_OR_REMOVE"
            )
        
        return success_response(
            data=UpdatedClassStudentsListData(
                added_students=students_list,
                removed_students=removed_students_list
            ),
            message="Students added to class successfully"
        )
    except Exception as e:
        logger.error(f"ADD_STUDENTS_TO_CLASS_ERROR: {e}")
        return error_response(
            message="Failed to add students to class",
            error_code="ADD_STUDENTS_TO_CLASS_ERROR"
        )