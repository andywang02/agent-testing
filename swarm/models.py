from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import uuid
import time

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SessionStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"

@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    content: str = ""
    timestamp: float = field(default_factory=time.time)
    processed: bool = False

@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    tmux_session_id: str = ""
    workspace_path: str = ""
    status: SessionStatus = SessionStatus.CREATED

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    repo_path: str = ""
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    parent_task_id: Optional[str] = None
