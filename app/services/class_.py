from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.user import user_repository
from app.schemas.student import UserStudent, StudentUpdate

async def add_students_to_class(db: AsyncSession, students: List[int], class_id: int) -> List[UserStudent]:
    students_list = []
    for student_id in students:
        student = await user_repository.get_user_student(db=db, user_id=student_id)
        if not student:
            continue
        else:
            if student.class_id != class_id:
                await user_repository.update(db=db, db_obj=student, obj_in=StudentUpdate(class_id=class_id))
                
                students_list.append({
                    "user_info": {
                        "id": student.user.id,
                        "email": student.user.email,
                        "username": student.user.username,
                        "full_name": student.user.full_name,
                        "is_active": student.user.is_active,
                        "role": student.user.role
                    },
                    "student_info": {
                        "class_id": student.class_id,
                        "parent_phone": student.parent_phone,
                        "parent_email": student.parent_email,
                        "parent_fio": student.parent_fio
                    }
            })
            
    return students_list

async def remove_students_from_class(db: AsyncSession, students: List[int], class_id: int) -> List[UserStudent]:
    removed_students_list = []
    for student_id in students:
        student = await user_repository.get_user_student(db=db, user_id=student_id)
        if not student:
            continue
        if student.class_id == class_id:
            await user_repository.update(db=db, db_obj=student, obj_in=StudentUpdate(class_id=None))
            removed_students_list.append({
                "user_info": {
                    "id": student.user.id,
                    "email": student.user.email,
                    "username": student.user.username,
                    "full_name": student.user.full_name,
                    "is_active": student.user.is_active,
                    "role": student.user.role
                },
                "student_info": {
                    "class_id": student.class_id,
                    "parent_phone": student.parent_phone,
                    "parent_email": student.parent_email,
                    "parent_fio": student.parent_fio
                }
            })
    return removed_students_list