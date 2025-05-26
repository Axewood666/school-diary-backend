from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.user import user_repository
from app.schemas.student import UserWithStudentInfo, StudentUpdate
from app.schemas.class_ import ClassCreate
from app.db.repositories.class_ import class_repository
from app.db.repositories.academic_cycles import academic_cycles_repository
from app.schemas.class_ import ClassConfig
from app.db.models.class_ import StudentClassHistoryReason

async def add_students_to_class(db: AsyncSession, students: List[int], class_id: int) -> List[UserWithStudentInfo]:
    students_list = []
    for student_id in students:
        student = await user_repository.get_user_student(db=db, user_id=student_id)
        if not student:
            continue
        else:
            if student.class_id != class_id:
                await user_repository.update(db=db, db_obj=student, obj_in=StudentUpdate(class_id=class_id))
                await class_repository.write_assign(db=db, student_id=student_id, class_id=class_id, reason=StudentClassHistoryReason.ADMISSION, is_active=True)

                students_list.append(UserWithStudentInfo.model_validate(student))
            
    return students_list

async def remove_students_from_class(db: AsyncSession, students: List[int], class_id: int) -> List[UserWithStudentInfo]:
    removed_students_list = []
    for student_id in students:
        student = await user_repository.get_user_student(db=db, user_id=student_id)
        if not student:
            continue
        if student.class_id == class_id:
            await user_repository.update(db=db, db_obj=student, obj_in=StudentUpdate(class_id=None))
            await class_repository.write_assign(db=db, student_id=student_id, class_id=None, reason=StudentClassHistoryReason.TRANSFER, is_active=True)
            
            removed_students_list.append(UserWithStudentInfo.model_validate(student))
    return removed_students_list

async def check_class_config(db: AsyncSession, class_create: ClassCreate, class_config: ClassConfig, class_id: int = None, class_year_id: int = None) -> bool:
        if class_create.grade_level not in class_config.grade_levels:
            raise ValueError("Invalid grade level")
        if class_create.letter not in class_config.letters:
            raise ValueError("Invalid letter")
        if class_create.specialization not in class_config.specializations:
            raise ValueError("Invalid specialization")
        if not class_year_id:
            year = await academic_cycles_repository.get_current_academic_year(db=db)
            if not year:
                raise ValueError("Year not found")
            class_year_id = year.id
        exist_letter = await class_repository.has_exist_class(db=db, letter=class_create.letter, grade_level=class_create.grade_level, year_id=class_year_id, class_id=class_id)
        if exist_letter:
            raise ValueError("Letter already exists")

        return True
