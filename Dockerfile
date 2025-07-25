FROM python:3.11-slim

WORKDIR /app

COPY fastapi_app/requirements.txt ./requirements.txt
COPY celery_worker/requirements.txt ./celery_requirements.txt

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r celery_requirements.txt

COPY fastapi_app /app/fastapi_app
COPY celery_worker /app/celery_worker
COPY shared /app/shared

# Entrypoint and command are set in docker-compose 