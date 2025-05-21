from pydantic import BaseModel

class Student(BaseModel):
    parent_phone: str = None
    parent_email: str = None
    parent_fio: str = None

class Teacher(BaseModel):
    degree: str = None
    experience: int = None
    bio: str = None

class Admin(BaseModel):
    pass

class StudentInDb(Student):
    user_id: int
    class_id: int = None

class TeacherInDb(Teacher):
    user_id: int
    class_id: int = None