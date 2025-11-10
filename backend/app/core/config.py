from pydantic import BaseSettings, AnyUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ozon Inventory Analytics"
    SECRET_KEY: str = "changeme"
    SQLALCHEMY_DATABASE_URI: AnyUrl = "postgresql+psycopg2://postgres:postgres@db:5432/postgres"
    REDIS_URL: str = "redis://redis:6379/0"
    TZ: str = "Europe/Warsaw"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FIRST_ADMIN_EMAIL: str = "admin@local"
    FIRST_ADMIN_PASSWORD: str = "admin123"
    TELEGRAM_BOT_TOKEN: str | None = None
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    SYNC_PERIOD_SECONDS: int = 10800
    DAILY_REPORT_SECONDS: int = 86400
    class Config:
        env_file = ".env"

settings = Settings()
