import unittest
import shutil
from pathlib import Path
from aflow.state import AflowState
import aflow.state
from aflow.allocator import TaskAllocator
from aflow.queue import TaskQueue

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.test_home = Path("/tmp/aflow_test_queue")
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        aflow.state.AFLOW_HOME = self.test_home
        aflow.state.STATE_FILE = self.test_home / "state.json"
        self.state = AflowState()
        self.allocator = TaskAllocator(self.state)
        self.queue = TaskQueue(self.state)

    def tearDown(self):
        if self.test_home.exists():
            shutil.rmtree(self.test_home)

    def test_task_creation_and_queue(self):
        task = self.allocator.create_task("Test Task", "Do something", "/tmp/dummy")
        self.assertIn(task.id, self.state.tasks)

        pending = self.queue.get_pending(task.id)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].content, "START: Do something")

        self.queue.mark_processed(pending[0].id)
        self.assertEqual(len(self.queue.get_pending(task.id)), 0)

if __name__ == "__main__":
    unittest.main()
