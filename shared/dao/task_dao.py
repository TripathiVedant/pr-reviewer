from shared.dao.session import SessionLocal
from shared.domains.domains import Task, TaskResult
from shared.models.enums import TaskStatus
import logging

logger = logging.getLogger("task_dao")


class TaskDAO:
    @staticmethod
    def get_by_id(task_id: str) -> Task | None:
        with SessionLocal() as session:
            return session.query(Task).filter(Task.task_id == task_id).first()

    @staticmethod
    def create(task: Task) -> Task:
        with SessionLocal() as session:
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def update_status(task_id: str, status: TaskStatus):
        with SessionLocal() as session:
            task = session.query(Task).filter(Task.task_id == task_id).first()
            if task:
                task.status = status
                session.commit()

    @staticmethod
    def get_by_repo_pr(repo_url: str, pr_number: int) -> Task | None:
        with SessionLocal() as session:
            return (
                session.query(Task)
                .filter(Task.repo_url == repo_url, Task.pr_number == pr_number)
                .first()
            )


    @staticmethod
    def store_results_and_update_status(task_id: str, results: dict, status: TaskStatus):
        """
        Store task results and update the task status in a single transaction.

        Args:
            task_id (str): The task ID.
            results (dict): The results to be stored.
            status (TaskStatus): The final status of the task.
        """
        with SessionLocal() as session:
            try:
                # Step 1: Store results in the database
                task_result = TaskResult(task_id=task_id, results=results)
                session.add(task_result)

                # Step 2: Update task status
                task = session.query(Task).filter(Task.task_id == task_id).first()
                if task:
                    task.status = status

                    # Step 3: Commit the transaction
                session.commit()
                logger.info(f"Results stored and task {task_id} status updated to {status}")
            except Exception as e:
                logger.error(f"Error during transaction for task {task_id}: {e}")
                session.rollback()
                raise