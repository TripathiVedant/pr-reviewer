from celery import Celery
from shared.config import settings

celery_app = Celery('fastapi_app', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND) 