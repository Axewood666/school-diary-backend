from typing import List
from app.schemas.base import PaginatedResponse
from app.schemas.auth.auth import Token, UserInviteInfo
from app.schemas.user.user import User
from app.schemas.user.student import UserWithStudentInfo
from app.schemas.user.teacher import UserWithTeacherInfo
from pydantic import BaseModel

class LoginSuccessResponse(Token):
    result: bool = True

class InviteListData(PaginatedResponse[UserInviteInfo]):
    pass

class UsersListData(PaginatedResponse[User]):
    pass

class StudentsListData(PaginatedResponse[UserWithStudentInfo]):
    pass

class UpdatedClassStudentsListData(BaseModel):
    added_students: List[UserWithStudentInfo]
    removed_students: List[UserWithStudentInfo]

class TeachersListData(PaginatedResponse[UserWithTeacherInfo]):
    pass

class AdminsListData(PaginatedResponse[User]):
    pass 