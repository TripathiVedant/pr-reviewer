from celery import Celery
from shared.config import settings

celery_app = Celery('celery_worker', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

app = celery_app  # Expose as 'app' for Celery CLI autodiscovery

worker_concurrency = settings.WORKER_CONCURRENCY
# worker_prefetch_multiplier = 1  # Improves task distribution among workers. (In our case, we have only 1 worker)
TASK_TIME_LIMIT = settings.TASK_TIME_LIMIT 

celery_app.autodiscover_tasks(['celery_worker']) 