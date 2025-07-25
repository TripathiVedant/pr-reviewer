from sqlalchemy import Column, String, Integer, Enum, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from shared.models.enums import PlatformType, TaskStatus
import uuid
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    platformType = Column(Enum(PlatformType), nullable=False)
    repo_url = Column(String, nullable=False)
    pr_number = Column(Integer, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskResult(Base):
    __tablename__ = "task_results"
    task_id = Column(String, ForeignKey("tasks.task_id"), primary_key=True)
    results = Column(JSON, nullable=False) 