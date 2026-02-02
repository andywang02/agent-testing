import unittest
import os
import shutil
from pathlib import Path
from swarm.models import Task, TaskStatus
from swarm.state import SwarmState, SWARM_HOME, STATE_FILE

class TestModels(unittest.TestCase):
    def setUp(self):
        # Use a temporary home for testing
        self.old_swarm_home = SWARM_HOME
        self.test_home = Path("/tmp/swarm_test")
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        import swarm.state
        swarm.state.SWARM_HOME = self.test_home
        swarm.state.STATE_FILE = self.test_home / "state.json"

    def tearDown(self):
        if self.test_home.exists():
            shutil.rmtree(self.test_home)

    def test_save_load_state(self):
        state = SwarmState()
        task = Task(name="Test Task", description="Testing models")
        state.tasks[task.id] = task
        state.save()

        new_state = SwarmState()
        self.assertIn(task.id, new_state.tasks)
        self.assertEqual(new_state.tasks[task.id].name, "Test Task")
        self.assertEqual(new_state.tasks[task.id].status, TaskStatus.PENDING)

if __name__ == "__main__":
    unittest.main()
