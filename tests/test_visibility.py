import unittest
import shutil
import os
from pathlib import Path
from aflow.state import AflowState
import aflow.state
from aflow.allocator import TaskAllocator
from aflow.models import TaskStatus

class TestVisibility(unittest.TestCase):
    def setUp(self):
        self.test_home = Path("/tmp/aflow_test_visibility")
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        aflow.state.AFLOW_HOME = self.test_home
        aflow.state.STATE_FILE = self.test_home / "state.json"
        self.state = AflowState()
        self.allocator = TaskAllocator(self.state)

    def tearDown(self):
        if self.test_home.exists():
            shutil.rmtree(self.test_home)

    def test_immediate_visibility(self):
        # Create a task
        task = self.allocator.create_task("Visible Task", "Test visibility", "/tmp/dummy")

        # Reload state to simulate another process/CLI call
        new_state = AflowState()

        # Verify task is present
        self.assertIn(task.id, new_state.tasks)

        # Verify session is ALREADY present
        sessions = [s for s in new_state.sessions.values() if s.task_id == task.id]
        self.assertEqual(len(sessions), 1, "Session should be registered immediately")

        print(f"Task {task.id} and Session {sessions[0].id} are both visible immediately.")

if __name__ == "__main__":
    unittest.main()
