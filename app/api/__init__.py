from fastapi import APIRouter

from app.api.v1 import auth, files

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(files.router, prefix="/files", tags=["files"]) 