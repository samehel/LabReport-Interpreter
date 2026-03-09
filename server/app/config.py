from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    DATABASE_URL: str = "sqlite+aiosqlite:///./lab_reports.db"
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    CORS_ORIGINS: str = "*"

    # Email / SMTP settings
    SMTP_ENABLED: bool = False  # Set to True once SMTP is configured
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = False
    SMTP_START_TLS: bool = True
    EMAIL_FROM_ADDRESS: str = "noreply@labreport.app"
    EMAIL_FROM_NAME: str = "LabReport Interpreter"
    OTP_EXPIRE_MINUTES: int = 10
    BASE_URL: str = "http://localhost:8000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
