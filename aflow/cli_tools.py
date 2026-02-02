import argparse
import os
import sys
from aflow.state import AflowState
from aflow.allocator import TaskAllocator

def spawn():
    parser = argparse.ArgumentParser(description="Spawn a sub-task from an agent session.")
    parser.add_argument("description", help="Description of the sub-task")
    parser.add_argument("--name", help="Name of the sub-task", default="Subtask")
    args = parser.parse_args()

    parent_task_id = os.environ.get("AFLOW_PARENT_TASK_ID")
    repo_path = os.environ.get("AFLOW_REPO_PATH")

    if not repo_path:
        print("Error: AFLOW_REPO_PATH not found in environment.")
        sys.exit(1)

    state = AflowState()
    allocator = TaskAllocator(state)

    task = allocator.create_task(
        name=args.name,
        description=args.description,
        repo_path=repo_path,
        parent_task_id=parent_task_id
    )

    print(f"Spawned sub-task {task.id}: {task.name}")

if __name__ == "__main__":
    spawn()
