from shared.domains.domains import TaskResult
from sqlalchemy.orm import Session

class TaskResultDAO:
    @staticmethod
    def get_by_task_id(session: Session, task_id: str) -> TaskResult:
        return session.query(TaskResult).filter(TaskResult.task_id == task_id).first()

    @staticmethod
    def create(session: Session, result: TaskResult) -> TaskResult:
        session.add(result)
        session.commit()
        return result 