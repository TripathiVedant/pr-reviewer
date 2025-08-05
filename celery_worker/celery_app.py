from celery import Celery
from shared.config import settings

# Configuration constants
BROKER_URL = settings.CELERY_BROKER_URL
RESULT_BACKEND = settings.CELERY_RESULT_BACKEND
WORKER_CONCURRENCY = settings.WORKER_CONCURRENCY
TASK_TIME_LIMIT = settings.TASK_TIME_LIMIT
# WORKER_PREFETCH_MULTIPLIER = 1  # Uncomment if you want more even distribution

# Create and configure Celery application
app = Celery(
    'celery_worker',
    broker=BROKER_URL,
    backend=RESULT_BACKEND
)

# Apply settings from constants
app.conf.update(
    worker_concurrency=WORKER_CONCURRENCY,
    task_time_limit=TASK_TIME_LIMIT,
    # worker_prefetch_multiplier=WORKER_PREFETCH_MULTIPLIER,
)

# Auto-discover tasks in the given packages
app.autodiscover_tasks(['celery_worker'])