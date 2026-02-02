import argparse
import os
import sys
from aflow.state import AflowState
from aflow.allocator import TaskAllocator
from aflow.models import WorkspaceStrategy

def spawn():
    parser = argparse.ArgumentParser(description="Spawn a sub-task from an agent session.")
    parser.add_argument("description", help="Description of the sub-task")
    parser.add_argument("--name", help="Name of the sub-task", default="Subtask")
    parser.add_argument("--strategy", choices=[s.value for s in WorkspaceStrategy],
                               default=WorkspaceStrategy.CLONE.value, help="Workspace strategy")
    parser.add_argument("--branch", help="Git branch (for worktree strategy)")
    args = parser.parse_args()

    parent_task_id = os.environ.get("AFLOW_PARENT_TASK_ID")
    repo_path = os.environ.get("AFLOW_REPO_PATH")

    if not repo_path:
        print("Error: AFLOW_REPO_PATH not found in environment.")
        sys.exit(1)

    state = AflowState()
    allocator = TaskAllocator(state)

    strategy = WorkspaceStrategy(args.strategy)
    task = allocator.create_task(
        name=args.name,
        description=args.description,
        repo_path=repo_path,
        strategy=strategy,
        branch=args.branch,
        parent_task_id=parent_task_id
    )

    # Get the session that was just created for this task
    sessions = [s for s in state.sessions.values() if s.task_id == task.id]
    session_id = sessions[0].id if sessions else "N/A"

    print(f"Spawned sub-task {task.id}: {task.name}")
    print(f"Associated session: {session_id}")
    print(f"Strategy: {strategy.value}")

if __name__ == "__main__":
    spawn()
