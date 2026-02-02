import unittest
import shutil
import os
import subprocess
from pathlib import Path
from aflow.state import AflowState
import aflow.state
from aflow.models import Task, WorkspaceStrategy
from aflow.session import SessionManager

class TestStrategies(unittest.TestCase):
    def setUp(self):
        self.test_home = Path("/tmp/aflow_test_strategies")
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        aflow.state.AFLOW_HOME = self.test_home
        aflow.state.STATE_FILE = self.test_home / "state.json"

        import aflow.session
        aflow.session.AFLOW_HOME = self.test_home

        self.state = AflowState()
        self.session_manager = SessionManager(self.state)

        # Create a source repo
        self.source_repo = Path("/tmp/source_repo")
        if self.source_repo.exists():
            shutil.rmtree(self.source_repo)
        self.source_repo.mkdir()
        subprocess.run(["git", "init"], cwd=self.source_repo)
        (self.source_repo / "main.txt").write_text("root")
        subprocess.run(["git", "add", "."], cwd=self.source_repo)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=self.source_repo)

    def tearDown(self):
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        if self.source_repo.exists():
            shutil.rmtree(self.source_repo)

    def test_repo_strategy(self):
        task = Task(name="Repo Task", repo_path=str(self.source_repo), strategy=WorkspaceStrategy.REPO)
        session = self.session_manager.register_session(task.id)
        self.session_manager.prepare_session(session, task)

        self.assertEqual(session.workspace_path, str(self.source_repo.absolute()))

    def test_clone_strategy(self):
        task = Task(name="Clone Task", repo_path=str(self.source_repo), strategy=WorkspaceStrategy.CLONE)
        session = self.session_manager.register_session(task.id)
        self.session_manager.prepare_session(session, task)

        self.assertNotEqual(session.workspace_path, str(self.source_repo.absolute()))
        self.assertTrue(os.path.exists(os.path.join(session.workspace_path, ".git")))
        self.assertTrue(os.path.exists(os.path.join(session.workspace_path, "main.txt")))

    def test_worktree_strategy(self):
        task = Task(name="Worktree Task", repo_path=str(self.source_repo), strategy=WorkspaceStrategy.WORKTREE)
        session = self.session_manager.register_session(task.id)
        self.session_manager.prepare_session(session, task)

        self.assertNotEqual(session.workspace_path, str(self.source_repo.absolute()))
        self.assertTrue(os.path.exists(os.path.join(session.workspace_path, ".git")))
        # In worktree, .git is a file pointing to the main repo's .git
        self.assertTrue(os.path.isfile(os.path.join(session.workspace_path, ".git")))

        # Verify branch was created
        res = subprocess.run(["git", "branch"], cwd=self.source_repo, capture_output=True, text=True)
        self.assertIn("aflow-tmp", res.stdout)

if __name__ == "__main__":
    unittest.main()
