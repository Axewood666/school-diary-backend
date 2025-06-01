from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

from app.db.models.user import UserRole
from app.db.repositories.file.file import file_repository
from app.schemas.file.file import File, FileCreate
from app.schemas.base import success_response, error_response
from app.services.minio import MinioService, get_minio_service
from app.core.dependencies import get_current_user
from app.schemas.user.user import User
import logging
from app.core.logger import setup_logging

setup_logging()
logger = logging.getLogger("app")

router = APIRouter(tags=["files"])

@router.post("/")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
    _: User = Depends(get_current_user)
):
    """
    Загрузка файла в хранилище с проверкой размера и типа.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        file_data = await file.read()
        file_size = len(file_data)
        if file_size > settings.MAX_FILE_SIZE: 
            return error_response(
                message=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE}MB",
                error_code="FILE_TOO_LARGE"
            )
        
        await file.seek(0)
        
        file.filename = minio_service._sanitize_filename(file.filename)
        object_name = await minio_service.upload_file(
            file=file
        )
        
        file_create = FileCreate(
            filename=object_name.split("/")[-1],
            original_filename=file.filename or "file",
            bucket_name=settings.MINIO_PUBLIC_BUCKET,
            object_name=object_name,
            content_type=file.content_type or "application/octet-stream",
            size=file_size,
        )
        
        db_file = await file_repository.create(db=db, obj_in=file_create)
        
        file_url = await minio_service.get_direct_file_url(
            bucket_name=settings.MINIO_PUBLIC_BUCKET,
            object_name=object_name
        )
        
        result = File.model_validate(db_file)
        result.url = file_url
        
        return success_response(
            data=result,
            message="File uploaded successfully"
        )
    except ValueError as e:
        logger.error(f"VALIDATION_ERROR: {e}")
        return error_response(
            message=str(e),
            error_code="VALIDATION_ERROR"
        )
    except Exception as e:
        logger.error(f"FILE_UPLOAD_ERROR: {e}")
        return error_response(
            message=f"Failed to upload file: {str(e)}",
            error_code="FILE_UPLOAD_ERROR"
        )

@router.get("/{file_id}")
async def get_file_by_id(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
    _: User = Depends(get_current_user),
):
    """
    Получение информации о файле с URL для прямого доступа.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    try:
        db_file = await file_repository.get(db=db, id=file_id)
        if not db_file:
            return error_response(
                message="File not found",
                error_code="FILE_NOT_FOUND"
            )
        
        file_url = await minio_service.get_direct_file_url(
            bucket_name=settings.MINIO_PUBLIC_BUCKET,
            object_name=db_file.object_name
        )
        
        result = File.model_validate(db_file)
        result.url = file_url
        
        return success_response(
            data=result,
            message="File retrieved successfully"
        )
    except Exception as e:
        logger.error(f"GET_FILE_ERROR: {e}")
        return error_response(
            message=f"Failed to retrieve file: {str(e)}",
            error_code="GET_FILE_ERROR"
        )

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    minio_service: MinioService = Depends(get_minio_service),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление файла из хранилища и базы данных.
    
    (Сгенерировано автоматически(C4S))@v1
    """
    if current_user.role != UserRole.ADMIN:
        return error_response(
            message="You are not allowed to delete files",
            error_code="INSUFFICIENT_PERMISSIONS"
        )
    try:
        db_file = await file_repository.get(db=db, id=file_id)
        if not db_file:
            return error_response(
                message="File not found",
                error_code="FILE_NOT_FOUND"
            )
        
        await minio_service.delete_file(
            bucket_name=db_file.bucket_name,
            object_name=db_file.object_name
        )
        
        await file_repository.remove(db=db, id=file_id)
        
        return success_response(
            data={"deleted": True},
            message="File deleted successfully"
        )
    except Exception as e:
        logger.error(f"DELETE_FILE_ERROR: {e}")
        return error_response(
            message=f"Failed to delete file: {str(e)}",
            error_code="DELETE_FILE_ERROR"
        )