from fastapi import APIRouter

from app.api.v1 import auth, files, users, class_, subject, academic_cycles

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(class_.router, prefix="/class", tags=["class"])
api_router.include_router(files.router, prefix="/files", tags=["files"]) 
api_router.include_router(subject.router, prefix="/subjects", tags=["subject"])
api_router.include_router(academic_cycles.router, prefix="/academic_cycles", tags=["academic_cycles"])