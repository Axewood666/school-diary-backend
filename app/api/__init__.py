from fastapi import APIRouter

from app.api.v1 import auth, files, users, class_, subjects, schedule, academic_cycles

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(class_.router, prefix="/class", tags=["class"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
api_router.include_router(academic_cycles.router, prefix="/academic-cycles", tags=["academic-cycles"]) 