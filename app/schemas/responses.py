from typing import List
from app.schemas.base import PaginatedResponse
from app.schemas.auth import Token, UserInviteInfo
from app.schemas.user import User
from app.schemas.student import UserWithStudentInfo
from app.schemas.teacher import UserWithTeacherInfo

class LoginSuccessResponse(Token):
    result: bool = True

class InviteListData(PaginatedResponse[UserInviteInfo]):
    pass

class UsersListData(PaginatedResponse[User]):
    pass

class StudentsListData(PaginatedResponse[UserWithStudentInfo]):
    pass

class TeachersListData(PaginatedResponse[UserWithTeacherInfo]):
    pass

class AdminsListData(PaginatedResponse[User]):
    pass 