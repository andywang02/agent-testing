from typing import Optional
from aflow.models import Task, TaskStatus, WorkspaceStrategy
from aflow.state import AflowState
from aflow.queue import TaskQueue
from aflow.session import SessionManager

class TaskAllocator:
    def __init__(self, state: AflowState):
        self.state = state
        self.queue = TaskQueue(state)
        self.session_manager = SessionManager(state)

    def create_task(self, name: str, description: str, repo_path: str,
                    strategy: WorkspaceStrategy = WorkspaceStrategy.CLONE,
                    branch: Optional[str] = None,
                    parent_task_id: Optional[str] = None) -> Task:
        task = Task(
            name=name,
            description=description,
            repo_path=repo_path,
            strategy=strategy,
            branch=branch,
            parent_task_id=parent_task_id,
            status=TaskStatus.PENDING
        )
        self.state.tasks[task.id] = task
        # No save here, register_session will save it

        # Register an initial session for this task immediately
        self.session_manager.register_session(task.id)

        # Initial message to start the task
        self.queue.put(task.id, f"START: {description}")

        return task

    def resume_task(self, task_id: str, instruction: str):
        if task_id not in self.state.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.state.tasks[task_id]
        if task.status == TaskStatus.COMPLETED:
            task.status = TaskStatus.RUNNING
            self.state.save()

        self.queue.put(task_id, f"RESUME: {instruction}")
