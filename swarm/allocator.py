from typing import Optional
from swarm.models import Task, TaskStatus
from swarm.state import SwarmState
from swarm.queue import TaskQueue

class TaskAllocator:
    def __init__(self, state: SwarmState):
        self.state = state
        self.queue = TaskQueue(state)

    def create_task(self, name: str, description: str, repo_path: str, parent_task_id: Optional[str] = None) -> Task:
        task = Task(
            name=name,
            description=description,
            repo_path=repo_path,
            parent_task_id=parent_task_id,
            status=TaskStatus.PENDING
        )
        self.state.tasks[task.id] = task
        self.state.save()

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
