import os
import subprocess
from pathlib import Path
from aflow.models import Session, SessionStatus, Task, WorkspaceStrategy
from aflow.state import AflowState, AFLOW_HOME

class SessionManager:
    def __init__(self, state: AflowState):
        self.state = state

    def register_session(self, task_id: str) -> Session:
        session = Session(task_id=task_id)
        session.tmux_session_id = f"aflow-{session.id[:8]}"
        self.state.sessions[session.id] = session
        self.state.save()
        return session

    def prepare_session(self, session: Session, task: Task):
        workspace_base = AFLOW_HOME / "workspaces" / session.id
        workspace_base.mkdir(parents=True, exist_ok=True)

        repo_dir = workspace_base / "repo"

        if task.strategy == WorkspaceStrategy.REPO:
            session.workspace_path = str(os.path.abspath(task.repo_path))

        elif task.strategy == WorkspaceStrategy.CLONE:
            # Clone the repo
            if not os.path.exists(task.repo_path):
                # Try to clone as URL
                subprocess.run(["git", "clone", task.repo_path, str(repo_dir)], check=True)
            else:
                # Local path, use shared clone if possible
                subprocess.run(["git", "clone", "--shared", task.repo_path, str(repo_dir)], check=True)
            session.workspace_path = str(repo_dir)

        elif task.strategy == WorkspaceStrategy.WORKTREE:
            if not os.path.exists(task.repo_path):
                raise ValueError(f"Worktree strategy requires a local repository path, got {task.repo_path}")

            branch = task.branch
            if not branch:
                # Create a temporary branch name
                branch = f"aflow-tmp-{session.id[:8]}"
                # Create the branch at the current HEAD of the source repo
                subprocess.run(["git", "branch", branch], cwd=task.repo_path, check=True)

            # Add worktree
            subprocess.run(["git", "worktree", "add", str(repo_dir), branch], cwd=task.repo_path, check=True)
            session.workspace_path = str(repo_dir)

        self.state.save()

    def start_session(self, session: Session, command: str, env: dict = None):
        # Start tmux session in background
        env_str = ""
        if env:
            for k, v in env.items():
                env_str += f"export {k}='{v}' && "

        subprocess.run([
            "tmux", "new-session", "-d", "-s", session.tmux_session_id,
            f"cd {session.workspace_path} && {env_str}{command}"
        ], check=True)

        session.status = SessionStatus.RUNNING
        self.state.save()

    def stop_session(self, session: Session):
        subprocess.run(["tmux", "kill-session", "-t", session.tmux_session_id], check=False)
        session.status = SessionStatus.STOPPED
        self.state.save()

    def send_to_session(self, session: Session, text: str):
        # Send keys to the tmux session
        subprocess.run(["tmux", "send-keys", "-t", session.tmux_session_id, text, "C-m"], check=True)
