from shared.dao.session import SessionLocal
from shared.domains.domains import TaskResult


class TaskResultDAO:
    @staticmethod
    def get_by_task_id(task_id: str) -> TaskResult | None:
        with SessionLocal() as session:
            return session.query(TaskResult).filter(TaskResult.task_id == task_id).first()

    @staticmethod
    def create(result: TaskResult) -> TaskResult:
        with SessionLocal() as session:
            session.add(result)
            session.commit()
            return result