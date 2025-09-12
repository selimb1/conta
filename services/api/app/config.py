from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "postgresql+psycopg://conta:conta@localhost:5432/conta"
    REDIS_URL: str = "redis://localhost:6379/0"
    STORAGE_DIR: str = "./storage"
    APP_NAME: str = "Conta API"

settings = Settings()