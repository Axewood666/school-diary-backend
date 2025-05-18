from fastapi import APIRouter

from app.api.v1 import auth, diary, files

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
# api_router.include_router(diary.router, prefix="/diary")
api_router.include_router(files.router, prefix="/files", tags=["files"]) 