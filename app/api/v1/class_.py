from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.base import error_response, BaseResponse, ErrorResponse, success_response
from app.schemas.user import UserRole, User
from app.schemas.responses import UpdatedClassStudentsListData

from app.core.dependencies import get_db
from app.core.logger import setup_logging
from app.db.models.user import User
from app.core.dependencies import get_current_user
from datetime import datetime
from app.db.repositories.class_ import (
    class_repository, student_class_history_repository, class_promotion_repository
)
from app.db.repositories.user import user_repository
from app.schemas.class_ import (
    ClassList, ClassCreate, ClassCreateDb, ClassUpdate, ClassWithStudents,
    StudentClassHistoryCreate, StudentClassHistoryList, StudentClassHistoryUpdate,
    ClassPromotionCreate, ClassPromotionList
)
import logging
from typing import List, Union, Optional
from app.db.repositories.academic_cycles import academic_cycles_repository
from app.services.class_ import add_students_to_class, remove_students_from_class

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["class"])

@router.get("/", response_model=Union[BaseResponse[List[ClassList]], ErrorResponse])
async def get_classes(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None, 
    order_by: str = "created_at", 
    order_direction: str = "desc", 
    year: int = datetime.now().year,
    grade_level: Optional[int] = Query(None, ge=1, le=11),
    with_students_count: bool = False,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Получить список классов"""
    try:
        if current_user.role == UserRole.TEACHER:
            teacher = await user_repository.get_user_teacher(db=db, user_id=current_user.id)
            classes = await class_repository.get_classes(
                db=db, teacher=teacher, search=search, order_by=order_by, 
                order_direction=order_direction, year=year, skip=skip, limit=limit,
                grade_level=grade_level
            )
        elif current_user.role == UserRole.ADMIN:
            classes = await class_repository.get_classes(
                db=db, search=search, order_by=order_by, order_direction=order_direction, 
                year=year, skip=skip, limit=limit, grade_level=grade_level
            )
        else:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        class_list = []
        for class_ in classes:
            if with_students_count:
                # Получаем класс с количеством студентов
                class_with_students = await class_repository.get_class_with_students_count(db=db, class_id=class_.id)
                students_count = len(class_with_students.students) if class_with_students and class_with_students.students else 0
                class_list.append(ClassWithStudents(
                    id=class_.id,
                    name=class_.name,
                    grade_level=class_.grade_level,
                    letter=class_.letter,
                    specialization=class_.specialization,
                    year_id=class_.year_id,
                    year_name=class_.year.name,
                    created_at=class_.created_at,
                    students_count=students_count
                ))
            else:
                class_list.append(ClassList(
                    id=class_.id,
                    name=class_.name,
                    grade_level=class_.grade_level,
                    letter=class_.letter,
                    specialization=class_.specialization,
                    year_id=class_.year_id,
                    year_name=class_.year.name,
                    created_at=class_.created_at,
                ))

        return success_response(
            data=class_list,
            message="Классы успешно получены"
        )
    except Exception as e:
        logger.error(f"GET_CLASS_ERROR: {e}")
        return error_response(
            message="Не удалось получить классы",
            error_code="GET_CLASS_ERROR"
        )
        
@router.post("/", response_model=Union[BaseResponse[ClassList], ErrorResponse])
async def create_class(
    class_create: ClassCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Создать новый класс"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
            
        year = await academic_cycles_repository.get_current_academic_year(db=db)
        if not year:
            return error_response(
                message="Текущий учебный год не найден",
                error_code="CURRENT_ACADEMIC_YEAR_NOT_FOUND"
            )

        class_ = await class_repository.create(db=db, obj_in=ClassCreateDb(
            name=class_create.name,
            grade_level=class_create.grade_level,
            letter=class_create.letter,
            specialization=class_create.specialization,
            year_id=year.id
        ))
        
        return success_response(
            data=ClassList(
                id=class_.id,
                name=class_.name,
                grade_level=class_.grade_level,
                letter=class_.letter,
                specialization=class_.specialization,
                year_id=class_.year_id,
                year_name=year.name,
                created_at=class_.created_at,
            ),
            message="Класс успешно создан"
        )
        
    except Exception as e:
        logger.error(f"CREATE_CLASS_ERROR: {e}")
        return error_response(
            message="Не удалось создать класс",
            error_code="CREATE_CLASS_ERROR"
        )

@router.get("/{class_id}", response_model=Union[BaseResponse[ClassWithStudents], ErrorResponse])
async def get_class(
    class_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить класс по ID"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        class_ = await class_repository.get_class_with_students_count(db=db, class_id=class_id)
        if not class_:
            return error_response(
                message="Класс не найден",
                error_code="CLASS_NOT_FOUND"
            )

        students_count = len(class_.students) if class_.students else 0

        return success_response(
            data=ClassWithStudents(
                id=class_.id,
                name=class_.name,
                grade_level=class_.grade_level,
                letter=class_.letter,
                specialization=class_.specialization,
                year_id=class_.year_id,
                year_name=class_.year.name,
                created_at=class_.created_at,
                students_count=students_count
            ),
            message="Класс успешно получен"
        )
    except Exception as e:
        logger.error(f"GET_CLASS_ERROR: {e}")
        return error_response(
            message="Не удалось получить класс",
            error_code="GET_CLASS_ERROR"
        )

@router.patch("/{class_id}", response_model=Union[BaseResponse[ClassList], ErrorResponse])
async def update_class(
    class_id: int, 
    class_update: ClassUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Обновить класс"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
            
        class_ = await class_repository.get(db=db, id=class_id)
        if not class_:
            return error_response(
                message="Класс не найден",
                error_code="CLASS_NOT_FOUND"
            )
        
        class_ = await class_repository.update(db=db, db_obj=class_, obj_in=class_update)
        class_year = await academic_cycles_repository.get_academic_year_by_id(db=db, id=class_.year_id)
        
        return success_response(
            data=ClassList(
                id=class_.id,
                name=class_.name,
                grade_level=class_.grade_level,
                letter=class_.letter,
                specialization=class_.specialization,
                year_id=class_.year_id,
                year_name=class_year.name if class_year else "Неизвестно",
                created_at=class_.created_at,
            ),
            message="Класс успешно обновлен"
        )
    except Exception as e:
        logger.error(f"UPDATE_CLASS_ERROR: {e}")
        return error_response(
            message="Не удалось обновить класс",
            error_code="UPDATE_CLASS_ERROR"
        )

@router.delete("/{class_id}", response_model=Union[BaseResponse[dict], ErrorResponse])
async def delete_class(
    class_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить класс"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        class_ = await class_repository.get(db=db, id=class_id)
        if not class_:
            return error_response(
                message="Класс не найден",
                error_code="CLASS_NOT_FOUND"
            )

        await class_repository.remove(db=db, id=class_id)

        return success_response(
            data={"deleted_id": class_id},
            message="Класс успешно удален"
        )
    except Exception as e:
        logger.error(f"DELETE_CLASS_ERROR: {e}")
        return error_response(
            message="Не удалось удалить класс",
            error_code="DELETE_CLASS_ERROR"
        )

@router.get("/grade/{grade_level}", response_model=Union[BaseResponse[List[ClassList]], ErrorResponse])
async def get_classes_by_grade(
    grade_level: int = Path(..., ge=1, le=11),
    year_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить классы по параллели"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        if not year_id:
            current_year = await academic_cycles_repository.get_current_academic_year(db=db)
            if current_year:
                year_id = current_year.id

        classes = await class_repository.get_classes_by_grade_level(
            db=db, grade_level=grade_level, year_id=year_id
        )

        class_list = []
        for class_ in classes:
            # Получаем год для каждого класса
            year = await academic_cycles_repository.get_academic_year_by_id(db=db, id=class_.year_id)
            class_list.append(ClassList(
                id=class_.id,
                name=class_.name,
                grade_level=class_.grade_level,
                letter=class_.letter,
                specialization=class_.specialization,
                year_id=class_.year_id,
                year_name=year.name if year else "Неизвестно",
                created_at=class_.created_at,
            ))

        return success_response(
            data=class_list,
            message="Классы по параллели успешно получены"
        )
    except Exception as e:
        logger.error(f"GET_CLASSES_BY_GRADE_ERROR: {e}")
        return error_response(
            message="Не удалось получить классы по параллели",
            error_code="GET_CLASSES_BY_GRADE_ERROR"
        )
        
@router.post("/{class_id}/students", response_model=Union[BaseResponse[UpdatedClassStudentsListData], ErrorResponse])
async def update_class_students(
    class_id: int, 
    new_students: List[int] = None, 
    remove_students: List[int] = None, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Добавить/удалить студентов из класса
    Input:
        - new_students: List[int] - Список ID студентов для добавления в класс
        - remove_students: List[int] - Список ID студентов для удаления из класса
    Output:
        - UpdatedClassStudentsListData - Добавленные и удаленные студенты с их информацией
    """
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        if not new_students and not remove_students:
            return error_response(
                message="Нет студентов для добавления или удаления",
                error_code="NO_STUDENTS_TO_ADD_OR_REMOVE"
            )
        
        class_ = await class_repository.get(db=db, id=class_id)
        if not class_:
            return error_response(
                message="Класс не найден",
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
                message="Нет студентов для добавления или удаления",
                error_code="NO_STUDENTS_TO_ADD_OR_REMOVE"
            )
        
        return success_response(
            data=UpdatedClassStudentsListData(
                added_students=students_list,
                removed_students=removed_students_list
            ),
            message="Студенты успешно добавлены/удалены из класса"
        )
    except Exception as e:
        logger.error(f"UPDATE_CLASS_STUDENTS_ERROR: {e}")
        return error_response(
            message="Не удалось обновить список студентов класса",
            error_code="UPDATE_CLASS_STUDENTS_ERROR"
        )

# Student Class History endpoints
@router.get("/{class_id}/history", response_model=Union[BaseResponse[List[StudentClassHistoryList]], ErrorResponse])
async def get_class_history(
    class_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить историю студентов класса"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        class_ = await class_repository.get(db=db, id=class_id)
        if not class_:
            return error_response(
                message="Класс не найден",
                error_code="CLASS_NOT_FOUND"
            )

        history = await student_class_history_repository.get_class_history(db=db, class_id=class_id)

        history_list = []
        for item in history:
            history_list.append(StudentClassHistoryList(
                id=item.id,
                student_id=item.student_id,
                student_name=item.student.user.full_name,
                class_id=item.class_id,
                class_name=item.class_.name,
                start_date=item.start_date,
                end_date=item.end_date,
                reason=item.reason,
                is_active=item.is_active,
                created_at=item.created_at
            ))

        return success_response(
            data=history_list,
            message="История класса успешно получена"
        )
    except Exception as e:
        logger.error(f"GET_CLASS_HISTORY_ERROR: {e}")
        return error_response(
            message="Не удалось получить историю класса",
            error_code="GET_CLASS_HISTORY_ERROR"
        )

@router.get("/student/{student_id}/history", response_model=Union[BaseResponse[List[StudentClassHistoryList]], ErrorResponse])
async def get_student_class_history(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить историю классов студента"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Проверяем существование студента
        student = await user_repository.get_user_student(db=db, user_id=student_id)
        if not student:
            return error_response(
                message="Студент не найден",
                error_code="STUDENT_NOT_FOUND"
            )

        history = await student_class_history_repository.get_student_history(db=db, student_id=student_id)

        history_list = []
        for item in history:
            history_list.append(StudentClassHistoryList(
                id=item.id,
                student_id=item.student_id,
                student_name=item.student.user.full_name,
                class_id=item.class_id,
                class_name=item.class_.name,
                start_date=item.start_date,
                end_date=item.end_date,
                reason=item.reason,
                is_active=item.is_active,
                created_at=item.created_at
            ))

        return success_response(
            data=history_list,
            message="История студента успешно получена"
        )
    except Exception as e:
        logger.error(f"GET_STUDENT_HISTORY_ERROR: {e}")
        return error_response(
            message="Не удалось получить историю студента",
            error_code="GET_STUDENT_HISTORY_ERROR"
        )

# Class Promotion endpoints
@router.get("/promotions", response_model=Union[BaseResponse[List[ClassPromotionList]], ErrorResponse])
async def get_class_promotions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить историю переводов классов"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        promotions = await class_promotion_repository.get_promotion_history(db=db, skip=skip, limit=limit)

        promotion_list = []
        for promotion in promotions:
            promotion_list.append(ClassPromotionList(
                id=promotion.id,
                from_class_id=promotion.from_class_id,
                from_class_name=promotion.from_class.name,
                to_class_id=promotion.to_class_id,
                to_class_name=promotion.to_class.name,
                promotion_date=promotion.promotion_date,
                created_at=promotion.created_at
            ))

        return success_response(
            data=promotion_list,
            message="История переводов успешно получена"
        )
    except Exception as e:
        logger.error(f"GET_CLASS_PROMOTIONS_ERROR: {e}")
        return error_response(
            message="Не удалось получить историю переводов",
            error_code="GET_CLASS_PROMOTIONS_ERROR"
        )

@router.post("/promotions", response_model=Union[BaseResponse[ClassPromotionList], ErrorResponse])
async def create_class_promotion(
    promotion_create: ClassPromotionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать перевод класса"""
    try:
        if current_user.role != UserRole.ADMIN:
            return error_response(
                message="У вас нет прав для доступа к этому ресурсу",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Проверяем существование классов
        from_class = await class_repository.get(db=db, id=promotion_create.from_class_id)
        if not from_class:
            return error_response(
                message="Исходный класс не найден",
                error_code="FROM_CLASS_NOT_FOUND"
            )

        to_class = await class_repository.get(db=db, id=promotion_create.to_class_id)
        if not to_class:
            return error_response(
                message="Целевой класс не найден",
                error_code="TO_CLASS_NOT_FOUND"
            )

        promotion = await class_promotion_repository.create(db=db, obj_in=promotion_create)

        return success_response(
            data=ClassPromotionList(
                id=promotion.id,
                from_class_id=promotion.from_class_id,
                from_class_name=from_class.name,
                to_class_id=promotion.to_class_id,
                to_class_name=to_class.name,
                promotion_date=promotion.promotion_date,
                created_at=promotion.created_at
            ),
            message="Перевод класса успешно создан"
        )
    except Exception as e:
        logger.error(f"CREATE_CLASS_PROMOTION_ERROR: {e}")
        return error_response(
            message="Не удалось создать перевод класса",
            error_code="CREATE_CLASS_PROMOTION_ERROR"
        )