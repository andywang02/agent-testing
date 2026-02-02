import json
import os
import time
import fcntl
from pathlib import Path
from typing import Dict, List
from aflow.models import Task, Session, Message, TaskStatus, SessionStatus

AFLOW_HOME = Path.home() / ".aflow"
STATE_FILE = AFLOW_HOME / "state.json"

class AflowState:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.sessions: Dict[str, Session] = {}
        self.messages: List[Message] = []
        self._ensure_home()
        self.load()

    def _ensure_home(self):
        AFLOW_HOME.mkdir(parents=True, exist_ok=True)
        (AFLOW_HOME / "workspaces").mkdir(parents=True, exist_ok=True)
        if not STATE_FILE.exists():
            with open(STATE_FILE, "w") as f:
                f.write("{}")

    def save(self):
        data = {
            "tasks": {k: self._serialize_task(v) for k, v in self.tasks.items()},
            "sessions": {k: self._serialize_session(v) for k, v in self.sessions.items()},
            "messages": [self._serialize_message(m) for m in self.messages]
        }
        # Use a+ to avoid truncation before lock
        with open(STATE_FILE, "a+") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def load(self):
        if not STATE_FILE.exists():
            return

        # Simple retry for concurrency
        for _ in range(5):
            f = None
            try:
                f = open(STATE_FILE, "r")
                fcntl.flock(f, fcntl.LOCK_SH)
                content = f.read()
                if not content:
                    time.sleep(0.1)
                    continue
                data = json.loads(content)
                self.tasks = {k: self._deserialize_task(v) for k, v in data.get("tasks", {}).items()}
                self.sessions = {k: self._deserialize_session(v) for k, v in data.get("sessions", {}).items()}
                self.messages = [self._deserialize_message(m) for m in data.get("messages", [])]
                return
            except (json.JSONDecodeError, IOError):
                time.sleep(0.1)
            finally:
                if f:
                    try:
                        fcntl.flock(f, fcntl.LOCK_UN)
                        f.close()
                    except:
                        pass

    def _serialize_task(self, t: Task) -> dict:
        return {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "repo_path": t.repo_path,
            "status": t.status.value,
            "created_at": t.created_at,
            "parent_task_id": t.parent_task_id
        }

    def _deserialize_task(self, d: dict) -> Task:
        return Task(
            id=d["id"],
            name=d["name"],
            description=d["description"],
            repo_path=d.get("repo_path", ""),
            status=TaskStatus(d["status"]),
            created_at=d["created_at"],
            parent_task_id=d.get("parent_task_id")
        )

    def _serialize_session(self, s: Session) -> dict:
        return {
            "id": s.id,
            "task_id": s.task_id,
            "tmux_session_id": s.tmux_session_id,
            "workspace_path": s.workspace_path,
            "status": s.status.value
        }

    def _deserialize_session(self, d: dict) -> Session:
        return Session(
            id=d["id"],
            task_id=d["task_id"],
            tmux_session_id=d["tmux_session_id"],
            workspace_path=d["workspace_path"],
            status=SessionStatus(d["status"])
        )

    def _serialize_message(self, m: Message) -> dict:
        return {
            "id": m.id,
            "task_id": m.task_id,
            "content": m.content,
            "timestamp": m.timestamp,
            "processed": m.processed
        }

    def _deserialize_message(self, d: dict) -> Message:
        return Message(
            id=d["id"],
            task_id=d["task_id"],
            content=d["content"],
            timestamp=d["timestamp"],
            processed=d.get("processed", False)
        )
