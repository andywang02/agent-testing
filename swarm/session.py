import os
import subprocess
from pathlib import Path
from swarm.models import Session, SessionStatus, Task
from swarm.state import SwarmState, SWARM_HOME

class SessionManager:
    def __init__(self, state: SwarmState):
        self.state = state

    def create_session(self, task: Task) -> Session:
        session = Session(task_id=task.id)
        workspace_base = SWARM_HOME / "workspaces" / session.id
        workspace_base.mkdir(parents=True, exist_ok=True)

        repo_dir = workspace_base / "repo"

        # Clone the repo
        if not os.path.exists(task.repo_path):
            # Try to clone as URL
             subprocess.run(["git", "clone", task.repo_path, str(repo_dir)], check=True)
        else:
            # Local path, use shared clone if possible
            subprocess.run(["git", "clone", "--shared", task.repo_path, str(repo_dir)], check=True)

        session.workspace_path = str(repo_dir)
        session.tmux_session_id = f"swarm-{session.id[:8]}"

        self.state.sessions[session.id] = session
        self.state.save()
        return session

    def start_session(self, session: Session, command: str, env: dict = None):
        # Start tmux session in background
        # -d: detached
        # -s: session name
        # command: the command to run

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
