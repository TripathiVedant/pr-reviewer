from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    DATABASE_URL: str
    WORKER_CONCURRENCY: int = 4
    TASK_TIME_LIMIT: int = 300

    class Config:
        env_file = ".env"

settings = Settings() 