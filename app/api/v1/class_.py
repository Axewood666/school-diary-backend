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
from app.schemas.class_ import ClassList, ClassCreate, ClassCreateDb, ClassUpdate, ClassConfig, ClassUpdateDb, ClassWithStudentsList
import logging
from typing import List, Union
from app.db.repositories.academic_cycles import academic_cycles_repository
from app.services.class_ import add_students_to_class, remove_students_from_class, check_class_config
from app.schemas.teacher import UserWithTeacherInfo, Teacher
from app.schemas.student import UserWithStudentInfo, Student
from app.schemas.user import UserResponse

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["class"])


@router.put("/config", response_model=Union[BaseResponse[ClassConfig], ErrorResponse])
async def update_class_config(class_config: ClassConfig, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        class_config = await class_repository.update_class_config(db=db, obj_in=class_config)
        
        return success_response(
            data=ClassConfig.model_validate(class_config),
            message="Class config updated successfully"
        )
        
    except Exception as e:
        logger.error(f"UPDATE_CLASS_CONFIG_ERROR: {e}")
        return error_response(
            message="Failed to update class config",
            error_code="UPDATE_CLASS_CONFIG_ERROR"
        )
        
@router.get("/config", response_model=Union[BaseResponse[ClassConfig], ErrorResponse])
async def get_class_config(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
            
        class_config = await class_repository.get_class_config(db=db)
        if not class_config:
            return error_response(
                message="Class config not found",
                error_code="CLASS_CONFIG_NOT_FOUND"
            )
        
        return success_response(
            data=ClassConfig.model_validate(class_config),
            message="Class config retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_CLASS_CONFIG_ERROR: {e}")
        return error_response(
            message="Failed to get class config",
            error_code="GET_CLASS_CONFIG_ERROR"
        )
        
@router.patch("/{class_id}/students", response_model=Union[BaseResponse[UpdatedClassStudentsListData], ErrorResponse])
async def update_class_students(class_id: int, new_students: List[int] = None, remove_students: List[int] = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        if (not new_students or len(new_students) == 0) and (not remove_students or len(remove_students) == 0):
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
            message="Class students updated successfully"
        )
    except Exception as e:
        logger.error(f"ADD_STUDENTS_TO_CLASS_ERROR: {e}")
        return error_response(
            message="Failed to add students to class",
            error_code="ADD_STUDENTS_TO_CLASS_ERROR"
        )
        
@router.get("/{class_id}/students", response_model=Union[BaseResponse[List[UserWithStudentInfo]], ErrorResponse])
async def get_class_students(class_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
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
            
        students = await user_repository.get_students(db=db, class_id=class_id, order_by="full_name", order_direction="asc")        
        students_list = []
        for student in students:
            student_data = UserWithStudentInfo(
                user_info=UserResponse.model_validate(student.user),
                student_info=Student.model_validate(student)
            )
            students_list.append(student_data)
            
        return success_response(
            data=students_list,
            message="Students retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_CLASS_STUDENTS_ERROR: {e}")
        return error_response(
            message="Failed to get class students",
            error_code="GET_CLASS_STUDENTS_ERROR"
        )
        
@router.get("/", response_model=Union[BaseResponse[List[ClassList]], ErrorResponse])
async def get_classes(skip: int = 0, limit: int = 100,
                        search: str = None,
                        order_by: str = "created_at", 
                        order_direction: str = "desc", 
                        year: int = datetime.now().year, 
                        db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
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
            teacher_data = None
            if class_.teacher and class_.teacher.user:
                teacher_data = UserWithTeacherInfo(
                    user_info=UserResponse.model_validate(class_.teacher.user),
                    teacher_info=Teacher.model_validate(class_.teacher)
                )
            
            class_list.append(ClassList(
                id=class_.id,
                name=class_.name,
                year_id=class_.year_id,
                students_count=class_.students_count,
                specialization=class_.specialization,
                year_name=class_.year.name,
                created_at=class_.created_at,
                teacher=teacher_data
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
            
        class_config = await class_repository.get_class_config(db=db)
        if not class_config:
            return error_response(
                message="Class config not found",
                error_code="CLASS_CONFIG_NOT_FOUND"
            )
        if not await check_class_config(db=db, class_create=class_create, class_config=class_config):
            return error_response(
                message="Invalid class config",
                error_code="INVALID_CLASS_CONFIG"
            )
        
        year = await academic_cycles_repository.get_current_academic_year(db=db)
        if not year:
            return error_response(
                message="Current academic year not found",
                error_code="CURRENT_ACADEMIC_YEAR_NOT_FOUND"
            )
        
        class_create_db = ClassCreateDb(
            grade_level=class_create.grade_level,
            letter=class_create.letter,
            specialization=class_create.specialization,
            year_id=year.id,
            name=f"{class_create.grade_level}{class_create.letter}"
        )

        class_ = await class_repository.create(db=db, obj_in=class_create_db)
        
        return success_response(
            data=ClassList(
                id=class_.id,
                name=class_.name,
                year_id=class_.year_id,
                year_name=year.name,
                created_at=class_.created_at,
                teacher=None
            ),
            message="Class created successfully"
        )
        
    except Exception as e:
        logger.error(f"CREATE_CLASS_ERROR: {e}")
        return error_response(
            message=f"Failed to create class {e}",
            error_code="CREATE_CLASS_ERROR"
        )

@router.get("/{class_id}", response_model=Union[BaseResponse[ClassWithStudentsList], ErrorResponse])
async def get_class_with_students(class_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="You are not allowed to access this resource",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        class_ = await class_repository.get_with_relations(db=db, id=class_id)
        if not class_:
            return error_response(
                message="Class not found",
                error_code="CLASS_NOT_FOUND"
            )
        
        students_list = []
        teacher_data = None
        
        if class_.students:
            for student in class_.students:
                students_list.append(UserWithStudentInfo(
                    user_info=UserResponse.model_validate(student.user),
                    student_info=Student.model_validate(student)
                ))
        
        if class_.teacher:
            teacher_data = UserWithTeacherInfo(
                user_info=UserResponse.model_validate(class_.teacher.user),
                teacher_info=Teacher.model_validate(class_.teacher)
            )
        
        return success_response(
                data=ClassWithStudentsList(
                    class_info=ClassList(
                        id=class_.id,
                        name=class_.name,
                        year_id=class_.year_id,
                        year_name=class_.year.name,
                        created_at=class_.created_at,
                        students_count=len(students_list) if students_list else 0,
                        specialization=class_.specialization
                    ),
                    students=students_list,
                    teacher=teacher_data
                ),
            message="Class retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_CLASS_ERROR: {e}")
        return error_response(
            message="Failed to get class",
            error_code="GET_CLASS_ERROR"
        )
        
@router.put("/{class_id}", response_model=Union[BaseResponse[ClassWithStudentsList], ErrorResponse])
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
            
        class_config = await class_repository.get_class_config(db=db)
        if not class_config:
            return error_response(
                message="Class config not found",
                error_code="CLASS_CONFIG_NOT_FOUND"
            )

        if not await check_class_config(db=db, class_create=class_update, class_config=class_config, class_id=class_id, class_year_id=class_.year_id):
            return error_response(
                message="Invalid class config",
                error_code="INVALID_CLASS_CONFIG"
            )

        class_update_db = ClassUpdateDb(
            grade_level=class_update.grade_level,
            letter=class_update.letter,
            specialization=class_update.specialization,
            name=f"{class_update.grade_level}{class_update.letter}"
        )   
        class_ = await class_repository.update(db=db, db_obj=class_, obj_in=class_update_db)
        
        class_ = await class_repository.get_with_relations(db=db, id=class_id)
        
        teacher_data = None
        students_list = []
        
        if class_.students:
            for student in class_.students:
                students_list.append(UserWithStudentInfo(
                    user_info=UserResponse.model_validate(student.user),
                    student_info=Student.model_validate(student)
                ))
        
        if class_.teacher:
            teacher_data = UserWithTeacherInfo(
                user_info=UserResponse.model_validate(class_.teacher.user),
                teacher_info=Teacher.model_validate(class_.teacher)
            )
        
        return success_response(
            data=ClassWithStudentsList(
                    class_info=ClassList(
                        id=class_.id,
                        name=class_.name,
                        year_id=class_.year_id,
                        year_name=class_.year.name,
                        created_at=class_.created_at,
                        students_count=len(students_list) if students_list else 0,
                        specialization=class_.specialization
                    ),
                    students=students_list,
                    teacher=teacher_data
                ),
            message="Class updated successfully"
        )
    except Exception as e:
        logger.error(f"UPDATE_CLASS_ERROR: {e}")
        return error_response(
            message="Failed to update class",
            error_code="UPDATE_CLASS_ERROR"
        )
        