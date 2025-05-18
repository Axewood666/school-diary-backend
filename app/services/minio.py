import uuid
from io import BytesIO
from typing import Optional, List, Dict, Any
import json

from fastapi import UploadFile, HTTPException
from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class MinioService:
    def __init__(
        self,
        endpoint: str = settings.MINIO_ENDPOINT,
        access_key: str = settings.MINIO_ACCESS_KEY,
        secret_key: str = settings.MINIO_SECRET_KEY,
        secure: bool = settings.MINIO_USE_HTTPS,
        external_endpoint: str = settings.MINIO_EXTERNAL_ENDPOINT
    ):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.external_endpoint = external_endpoint
        self.secure = secure
        
    async def ensure_bucket_exists(self, bucket_name: str, make_public: bool = False) -> None:
        """Проверяет существование бакета и создает его при необходимости"""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                
                if make_public:
                    policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"AWS": "*"},
                                "Action": ["s3:GetObject"],
                                "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                            }
                        ]
                    }
                    self.client.set_bucket_policy(bucket_name, json.dumps(policy))
        except S3Error as err:
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка при создании бакета: {err}"
            )
    
    async def upload_file(
        self, 
        file: UploadFile, 
        bucket_name: str = settings.MINIO_PUBLIC_BUCKET,
        folder: str = "",
        metadata: Optional[Dict[str, str]] = None,
        make_public: bool = True
    ) -> str:
        """Загружает файл в MinIO и возвращает путь к файлу.
        Параметр make_public позволяет создать публичный бакет при загрузке.
        """
        try:
            await self.ensure_bucket_exists(bucket_name, make_public=make_public)
            
            # Генерация уникального имени файла
            original_filename = file.filename or "file"
            file_name = f"{original_filename}-{uuid.uuid4()}"
            
            # Добавляем префикс папки, если указан
            if folder:
                object_name = f"{folder}/{file_name}"
            else:
                object_name = file_name
            
            # Подготовка файла для загрузки
            file_data = await file.read()
            file_size = len(file_data)
            
            # Загрузка файла
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=BytesIO(file_data),
                length=file_size,
                content_type=file.content_type,
                metadata=metadata
            )
            
            return object_name
        except S3Error as err:
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка при загрузке файла: {err}"
            )
    
    async def download_file(
        self, 
        bucket_name: str, 
        object_name: str
    ) -> tuple[BytesIO, str, int]:
        """Скачивает файл из MinIO и возвращает его содержимое, имя и размер"""
        try:
            # Получаем метаданные объекта
            stat = self.client.stat_object(bucket_name, object_name)
            
            # Скачиваем объект
            response = self.client.get_object(bucket_name, object_name)
            
            # Читаем содержимое в память
            data = BytesIO(response.read())
            
            # Не забываем закрыть соединение
            response.close()
            response.release_conn()
            
            # Возвращаем содержимое, имя и размер файла
            filename = object_name.split("/")[-1]
            return data, filename, stat.size
        except S3Error as err:
            raise HTTPException(
                status_code=404 if "not found" in str(err).lower() else 500,
                detail=f"Ошибка при скачивании файла: {err}"
            )
    
    async def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """Удаляет файл из MinIO"""
        try:
            self.client.remove_object(bucket_name, object_name)
            return True
        except S3Error as err:
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка при удалении файла: {err}"
            )
    
    async def get_direct_file_url(
        self,
        bucket_name: str,
        object_name: str
    ) -> str:
        """Генерирует прямую URL-ссылку для доступа к файлу"""
        try:
            # Прямая ссылка строится по шаблону: http(s)://<endpoint>/<bucket>/<object>
            protocol = "https" if self.secure else "http"
            return f"{protocol}://{self.external_endpoint}/{bucket_name}/{object_name}"
        except Exception as err:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при создании прямой ссылки: {str(err)}"
            )
    
    async def list_files(
        self, 
        bucket_name: str, 
        prefix: str = "", 
        recursive: bool = True
    ) -> List[Dict[str, Any]]:
        """Получает список файлов в бакете с заданным префиксом"""
        try:
            await self.ensure_bucket_exists(bucket_name)
            
            objects = self.client.list_objects(
                bucket_name=bucket_name,
                prefix=prefix,
                recursive=recursive
            )
            
            return [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                } 
                for obj in objects
            ]
        except S3Error as err:
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка при получении списка файлов: {err}"
            )
    
    async def check_if_file_exists(self, bucket_name: str, object_name: str) -> bool:
        """Проверяет существование файла в MinIO"""
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False


minio_service = MinioService()


def get_minio_service() -> MinioService:
    return minio_service