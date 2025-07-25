from shared.domains.domains import Task
from sqlalchemy.orm import Session
from shared.models.enums import TaskStatus

class TaskDAO:
    @staticmethod
    def get_by_id(session: Session, task_id: str) -> Task:
        return session.query(Task).filter(Task.task_id == task_id).first()

    @staticmethod
    def create(session: Session, task: Task) -> Task:
        session.add(task)
        session.commit()
        return task

    @staticmethod
    def update_status(session: Session, task_id: str, status: TaskStatus):
        task = session.query(Task).filter(Task.task_id == task_id).first()
        if task:
            task.status = status
            session.commit()
        return task 