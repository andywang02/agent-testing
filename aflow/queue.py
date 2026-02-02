from typing import List, Optional
from aflow.models import Message
from aflow.state import AflowState

class TaskQueue:
    def __init__(self, state: AflowState):
        self.state = state

    def put(self, task_id: str, content: str) -> Message:
        message = Message(task_id=task_id, content=content)
        self.state.messages.append(message)
        self.state.save()
        return message

    def get_pending(self, task_id: str) -> List[Message]:
        return [m for m in self.state.messages if m.task_id == task_id and not m.processed]

    def mark_processed(self, message_id: str):
        for m in self.state.messages:
            if m.id == message_id:
                m.processed = True
                break
        self.state.save()
