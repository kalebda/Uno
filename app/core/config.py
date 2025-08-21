from typing import Any, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    DEPLOYMENT: str = "local"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        return f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"

    # Groq API Configuration
    GROQ_API_KEY: Optional[str] = None

    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = None

    # Application
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Study Abroad AI Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "*"
    ]

    # User Management
    DEFAULT_USER_EMAIL: str = "default@example.com"
    DEFAULT_USER_NAME: str = "Default User"
    DEFAULT_USER_ACTIVE: bool = True
    DEFAULT_USER_SUPERUSER: bool = False

    # Vector Database
    VECTOR_DB_PATH: str = "./data/vector_db"

    # Scraping
    SCRAPING_DELAY: int = 2
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    class Config:
        env_file = ".env"


settings = Settings()
