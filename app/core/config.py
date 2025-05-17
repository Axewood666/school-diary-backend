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
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings() 