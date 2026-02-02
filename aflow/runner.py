import os
import time
import threading
from typing import Dict, List
from aflow.models import Task, TaskStatus, Session
from aflow.state import AflowState
from aflow.queue import TaskQueue
from aflow.session import SessionManager

class TaskRunner:
    def __init__(self, state: AflowState, task_id: str):
        self.state = state
        self.task_id = task_id
        self.queue = TaskQueue(state)
        self.session_manager = SessionManager(state)
        self.running = False
        self._thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self):
        task = self.state.tasks.get(self.task_id)
        if not task:
            return

        task.status = TaskStatus.RUNNING
        self.state.save()

        # Ensure at least one session exists
        sessions = [s for s in self.state.sessions.values() if s.task_id == self.task_id]
        if not sessions:
            session = self.session_manager.create_session(task)
            # For now, let's assume we run "claude" by default.
            # In a real app, this would be configurable.
            # For testing, we might want to override this.
            env = {
                "AFLOW_PARENT_TASK_ID": self.task_id,
                "AFLOW_REPO_PATH": task.repo_path
            }
            self.session_manager.start_session(
                session,
                os.environ.get("AFLOW_COMMAND", "claude"),
                env=env
            )
            sessions = [session]

        while self.running:
            pending_messages = self.queue.get_pending(self.task_id)
            for msg in pending_messages:
                print(f"Task {self.task_id} processing message: {msg.content}")
                # Pass information to all sessions for this task
                for session in sessions:
                    self.session_manager.send_to_session(session, msg.content)
                self.queue.mark_processed(msg.id)

            time.sleep(1)

class AflowDaemon:
    def __init__(self, state: AflowState):
        self.state = state
        self.runners: Dict[str, TaskRunner] = {}
        self.running = False

    def start(self):
        self.running = True
        while self.running:
            self.state.load() # Refresh state
            for task_id, task in self.state.tasks.items():
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    if task_id not in self.runners:
                        print(f"Starting/Resuming runner for task {task_id}")
                        runner = TaskRunner(self.state, task_id)
                        self.runners[task_id] = runner
                        runner.start()
            time.sleep(2)

    def stop(self):
        self.running = False
        for runner in self.runners.values():
            runner.stop()
