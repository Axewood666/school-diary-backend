from pydantic_settings import BaseSettings
import os
from pydantic import model_validator
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "School API")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    PORT: int = os.getenv("PORT", 8000)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_URL_MIGRATE: str = os.getenv("DATABASE_URL_MIGRATE")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", 'temp_secret')
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 600)
    
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_PUBLIC_BUCKET: str = os.getenv("MINIO_PUBLIC_BUCKET", "public")
    MINIO_USE_HTTPS: bool = os.getenv("MINIO_USE_HTTPS", "false").lower() == "true"
    MINIO_REDIRECT_USE_HTTPS: bool = os.getenv("MINIO_REDIRECT_USE_HTTPS", "false").lower() == "true"
    MINIO_EXTERNAL_ENDPOINT: str = os.getenv("MINIO_EXTERNAL_ENDPOINT", "")
    MAX_FILE_SIZE: int = os.getenv("MAX_FILE_SIZE", 52428800)
    
    @model_validator(mode='after')
    def set_minio_external_endpoint(self) -> 'Settings':
        if not self.MINIO_EXTERNAL_ENDPOINT:
            self.MINIO_EXTERNAL_ENDPOINT = self.MINIO_ENDPOINT
        return self

    MAIL_USERNAME: Optional[str] = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: Optional[str] = os.getenv("MAIL_FROM")
    MAIL_PORT: Optional[int] = os.getenv("MAIL_PORT")
    MAIL_SERVER: Optional[str] = os.getenv("MAIL_SERVER")
    MAIL_STARTTLS: Optional[bool] = os.getenv("MAIL_STARTTLS")
    MAIL_SSL_TLS: Optional[bool] = os.getenv("MAIL_SSL_TLS")
    USE_CREDENTIALS: Optional[bool] = os.getenv("USE_CREDENTIALS")
    VALIDATE_CERTS: Optional[bool] = os.getenv("VALIDATE_CERTS")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings() 