import unittest
import os
import shutil
from pathlib import Path
from aflow.models import Task, TaskStatus
from aflow.state import AflowState, AFLOW_HOME, STATE_FILE

class TestModels(unittest.TestCase):
    def setUp(self):
        # Use a temporary home for testing
        self.old_aflow_home = AFLOW_HOME
        self.test_home = Path("/tmp/aflow_test")
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        import aflow.state
        aflow.state.AFLOW_HOME = self.test_home
        aflow.state.STATE_FILE = self.test_home / "state.json"

    def tearDown(self):
        if self.test_home.exists():
            shutil.rmtree(self.test_home)

    def test_save_load_state(self):
        state = AflowState()
        task = Task(name="Test Task", description="Testing models")
        state.tasks[task.id] = task
        state.save()

        new_state = AflowState()
        self.assertIn(task.id, new_state.tasks)
        self.assertEqual(new_state.tasks[task.id].name, "Test Task")
        self.assertEqual(new_state.tasks[task.id].status, TaskStatus.PENDING)

if __name__ == "__main__":
    unittest.main()
