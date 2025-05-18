from pydantic_settings import BaseSettings
import os
from pydantic import model_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    API_V1_STR: str = os.getenv("API_V1_STR")
    PORT: int = os.getenv("PORT")
    # FRONTEND_URL: str = os.getenv("FRONTEND_URL")
    # Подключение к БД
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_URL_MIGRATE: str = os.getenv("DATABASE_URL_MIGRATE")
    
    # JWT токены
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # MinIO настройки
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_PUBLIC_BUCKET: str = os.getenv("MINIO_PUBLIC_BUCKET", "public")
    MINIO_USE_HTTPS: bool = os.getenv("MINIO_USE_HTTPS", "false").lower() == "true"
    MINIO_EXTERNAL_ENDPOINT: str = os.getenv("MINIO_EXTERNAL_ENDPOINT", "")

    @model_validator(mode='after')
    def set_minio_external_endpoint(self) -> 'Settings':
        if not self.MINIO_EXTERNAL_ENDPOINT:
            self.MINIO_EXTERNAL_ENDPOINT = self.MINIO_ENDPOINT
        return self

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings() 