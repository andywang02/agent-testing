import unittest
import shutil
import os
import subprocess
import time
from pathlib import Path
from swarm.state import SwarmState
import swarm.state
from swarm.models import Task
from swarm.session import SessionManager

class TestSession(unittest.TestCase):
    def setUp(self):
        self.test_home = Path("/tmp/swarm_test_session")
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        swarm.state.SWARM_HOME = self.test_home
        swarm.state.STATE_FILE = self.test_home / "state.json"
        self.state = SwarmState()
        self.session_manager = SessionManager(self.state)

        # Create a dummy repo to clone
        self.dummy_repo = Path("/tmp/dummy_repo")
        if self.dummy_repo.exists():
            shutil.rmtree(self.dummy_repo)
        self.dummy_repo.mkdir()
        subprocess.run(["git", "init"], cwd=self.dummy_repo)
        (self.dummy_repo / "README.md").write_text("Hello")
        subprocess.run(["git", "add", "."], cwd=self.dummy_repo)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=self.dummy_repo)

    def tearDown(self):
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        if self.dummy_repo.exists():
            shutil.rmtree(self.dummy_repo)
        # Kill any leaked tmux sessions
        subprocess.run(["pkill", "-f", "swarm-"], check=False)

    def test_create_and_start_session(self):
        task = Task(name="Test Task", repo_path=str(self.dummy_repo))
        session = self.session_manager.create_session(task)

        self.assertTrue(os.path.exists(session.workspace_path))
        self.assertTrue(os.path.exists(os.path.join(session.workspace_path, ".git")))

        mock_claude_path = os.path.abspath("tests/mock_claude.py")
        self.session_manager.start_session(session, f"python3 {mock_claude_path}")

        # Give it a second to start
        time.sleep(1)

        # Check if tmux session exists
        res = subprocess.run(["tmux", "has-session", "-t", session.tmux_session_id])
        self.assertEqual(res.returncode, 0)

        # Send a command
        self.session_manager.send_to_session(session, "hello from test")
        time.sleep(1)

        # Cleanup
        self.session_manager.stop_session(session)
        res = subprocess.run(["tmux", "has-session", "-t", session.tmux_session_id])
        self.assertNotEqual(res.returncode, 0)

if __name__ == "__main__":
    unittest.main()
