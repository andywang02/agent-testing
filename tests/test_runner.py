import unittest
import shutil
import os
import subprocess
import time
import threading
from pathlib import Path
from aflow.state import AflowState
import aflow.state
from aflow.allocator import TaskAllocator
from aflow.runner import TaskRunner, AflowDaemon
from aflow.models import TaskStatus

class TestRunner(unittest.TestCase):
    def setUp(self):
        self.test_home = Path("/tmp/aflow_test_runner")
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        aflow.state.AFLOW_HOME = self.test_home
        aflow.state.STATE_FILE = self.test_home / "state.json"
        self.state = AflowState()
        self.allocator = TaskAllocator(self.state)

        # Create a dummy repo
        self.dummy_repo = Path("/tmp/dummy_repo_runner")
        if self.dummy_repo.exists():
            shutil.rmtree(self.dummy_repo)
        self.dummy_repo.mkdir()
        subprocess.run(["git", "init"], cwd=self.dummy_repo)
        (self.dummy_repo / "README.md").write_text("Hello")
        subprocess.run(["git", "add", "."], cwd=self.dummy_repo)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=self.dummy_repo)

        # Set mock command
        os.environ["AFLOW_COMMAND"] = f"python3 {os.path.abspath('tests/mock_claude.py')}"

    def tearDown(self):
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        if self.dummy_repo.exists():
            shutil.rmtree(self.dummy_repo)
        subprocess.run(["pkill", "-f", "aflow-"], check=False)

    def test_end_to_end_runner(self):
        task = self.allocator.create_task("Runner Task", "End to end test", str(self.dummy_repo))

        daemon = AflowDaemon(self.state)
        daemon_thread = threading.Thread(target=daemon.start, daemon=True)
        daemon_thread.start()

        # Wait for task to be picked up and session created
        max_wait = 15
        sessions = []
        while max_wait > 0:
            self.state.load()
            sessions = [s for s in self.state.sessions.values() if s.task_id == task.id]
            if self.state.tasks[task.id].status == TaskStatus.RUNNING and sessions:
                break
            time.sleep(1)
            max_wait -= 1

        self.assertEqual(self.state.tasks[task.id].status, TaskStatus.RUNNING)
        self.assertTrue(len(sessions) > 0)

        # Send a message via allocator (resuming)
        self.allocator.resume_task(task.id, "Second message")

        # Wait for message to be processed
        time.sleep(3)

        pending = [m for m in self.state.messages if m.task_id == task.id and not m.processed]
        self.assertEqual(len(pending), 0)

        daemon.stop()

if __name__ == "__main__":
    unittest.main()
