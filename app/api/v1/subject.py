from fastapi import APIRouter

from app.schemas.subject import SubjectList, SubjectCreate, SubjectUpdate, TeacherWithSubjects
from app.schemas.base import BaseResponse, ErrorResponse, success_response, error_response
from app.schemas.teacher import UserWithTeacherInfo, Teacher
from app.schemas.user import UserResponse

from app.db.repositories.subject import subject_repository
from app.db.repositories.user import user_repository
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from fastapi import Depends

import logging
from app.core.logger import setup_logging

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["subject"])

@router.get("/", response_model=Union[BaseResponse[List[SubjectList]], ErrorResponse])
async def get_subjects(skip: int = 0, limit: int = 100, 
                        search: str = None, 
                        order_by: str = "created_at", order_direction: str = "desc", 
                        is_active: bool = True,
                        db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        subjects = await subject_repository.get_all(db=db, skip=skip, limit=limit, search=search, order_by=order_by, order_direction=order_direction, is_active=is_active)
        return success_response(data=subjects, message="Subjects retrieved successfully")
    except Exception as e:
        logger.error(f"GET_SUBJECTS_ERROR: {e}")
        return error_response(message="Failed to get subjects", error_code="GET_SUBJECTS_ERROR")
    
@router.post("/", response_model=Union[BaseResponse[SubjectList], ErrorResponse])
async def create_subject(subject: SubjectCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
            
        subject = await subject_repository.create(db=db, subject=subject)
        
        return success_response(data=subject, message="Subject created successfully")
    except Exception as e:
        logger.error(f"CREATE_SUBJECT_ERROR: {e}")
        return error_response(message="Failed to create subject", error_code="CREATE_SUBJECT_ERROR")

@router.patch("/{subject_id}", response_model=Union[BaseResponse[SubjectList], ErrorResponse])
async def update_subject(subject_id: int, subject: SubjectUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        subject_db = await subject_repository.get(db=db, id=subject_id)
        if not subject_db:
            return error_response(message="Subject not found", error_code="SUBJECT_NOT_FOUND")
        
        subject = await subject_repository.update(db=db, db_obj=subject_db, obj_in=subject)
        return success_response(data=subject, message="Subject updated successfully")
    except Exception as e:
        logger.error(f"UPDATE_SUBJECT_ERROR: {e}")
        return error_response(message="Failed to update subject", error_code="UPDATE_SUBJECT_ERROR")
    
@router.delete("/{subject_id}", response_model=Union[BaseResponse[None], ErrorResponse])
async def delete_subject(subject_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS")
        subject = await subject_repository.get(db=db, id=subject_id)
        if not subject:
            return error_response(message="Subject not found", error_code="SUBJECT_NOT_FOUND")
        if not subject.is_active:
            return error_response(message="Subject is not active", error_code="SUBJECT_IS_NOT_ACTIVE")
        
        await subject_repository.update(db=db, db_obj=subject, obj_in=SubjectUpdate(is_active=False))
        return success_response(data=None, message="Subject deleted successfully")
    except Exception as e:
        logger.error(f"DELETE_SUBJECT_ERROR: {e}")
        return error_response(message="Failed to delete subject", error_code="DELETE_SUBJECT_ERROR")

@router.get("/{subject_id}/teachers", response_model=Union[BaseResponse[List[UserWithTeacherInfo]], ErrorResponse])
async def get_subject_teachers(subject_id: int,
                                skip: int = 0, limit: int = 100,
                                db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        teacher_subjects = await subject_repository.get_teachers_by_subject(db=db, subject_id=subject_id, skip=skip, limit=limit)
        if not teacher_subjects:
            return error_response(message="Subject teachers not found", error_code="SUBJECT_TEACHERS_NOT_FOUND")
        
        teachers_list = []
        for teacher_subject in teacher_subjects:
            teacher_info = UserWithTeacherInfo(
                user_info=UserResponse.model_validate(teacher_subject.teacher.user),
                teacher_info=Teacher.model_validate(teacher_subject.teacher)
            )
            teachers_list.append(teacher_info)
            
        return success_response(data=teachers_list, message="Subject teachers retrieved successfully")
    except Exception as e:
        logger.error(f"GET_SUBJECT_TEACHERS_ERROR: {e}")
        return error_response(message="Failed to get subject teachers", error_code="GET_SUBJECT_TEACHERS_ERROR")
    
@router.get("/{subject_id}", response_model=Union[BaseResponse[SubjectList], ErrorResponse])
async def get_subject(subject_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        subject = await subject_repository.get(db=db, id=subject_id)
        if not subject:
            return error_response(message="Subject not found", error_code="SUBJECT_NOT_FOUND")
        
        return success_response(data=subject, message="Subject retrieved successfully")
    except Exception as e:
        logger.error(f"GET_SUBJECT_ERROR: {e}")
        return error_response(message="Failed to get subject", error_code="GET_SUBJECT_ERROR")
    
@router.post("/{subject_id}/teachers", response_model=Union[BaseResponse[TeacherWithSubjects], ErrorResponse])
async def add_subject_teacher(subject_id: int, teacher_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS")
            
        subject = await subject_repository.get(db=db, id=subject_id)
        if not subject:
            return error_response(message="Subject not found", error_code="SUBJECT_NOT_FOUND")
        
        teacher = await user_repository.get_user_teacher(db=db, user_id=teacher_id)
        if not teacher:
            return error_response(message="Teacher not found", error_code="TEACHER_NOT_FOUND")
        
        if await subject_repository.get_teacher_subject(db=db, subject_id=subject_id, teacher_id=teacher_id):
            return error_response(message="Teacher already in subject", error_code="TEACHER_ALREADY_IN_SUBJECT")
        
        await subject_repository.add_teacher_subject(db=db, subject_id=subject_id, teacher_id=teacher_id)
        
        subjects = await subject_repository.get_subjects_by_teacher(db=db, teacher_id=teacher_id)
        subjects_list = []
        for subject_item in subjects:
            subjects_list.append(SubjectList.model_validate(subject_item))
        teacher_with_subject = TeacherWithSubjects(
            teacher=UserWithTeacherInfo(
                user_info=UserResponse.model_validate(teacher.user),
                teacher_info=Teacher.model_validate(teacher)
            ),
            subject=subjects_list
        )
        return success_response(data=teacher_with_subject, message="Teacher added to subject successfully")
    except Exception as e:
        logger.error(f"ADD_SUBJECT_TEACHER_ERROR: {e}")
        return error_response(message="Failed to add teacher to subject", error_code="ADD_SUBJECT_TEACHER_ERROR")
    
@router.get("/{teacher_id}/subjects", response_model=Union[BaseResponse[List[SubjectList]], ErrorResponse])
async def get_teacher_subjects(teacher_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        teacher = await user_repository.get_user_teacher(db=db, user_id=teacher_id)
        if not teacher:
            return error_response(message="Teacher not found", error_code="TEACHER_NOT_FOUND")
        
        teacher_subjects = await subject_repository.get_subjects_by_teacher(db=db, teacher_id=teacher_id)
        if not teacher_subjects:
            return error_response(message="Teacher subjects not found", error_code="TEACHER_SUBJECTS_NOT_FOUND")
        
        subjects_list = []
        for subject_item in teacher_subjects:
            subjects_list.append(SubjectList.model_validate(subject_item))

        return success_response(data=subjects_list, message="Teacher subjects retrieved successfully")
    except Exception as e:
        logger.error(f"GET_TEACHER_SUBJECTS_ERROR: {e}")