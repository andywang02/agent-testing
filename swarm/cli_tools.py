import argparse
import os
import sys
from swarm.state import SwarmState
from swarm.allocator import TaskAllocator

def spawn():
    parser = argparse.ArgumentParser(description="Spawn a sub-task from an agent session.")
    parser.add_argument("description", help="Description of the sub-task")
    parser.add_argument("--name", help="Name of the sub-task", default="Subtask")
    args = parser.parse_args()

    parent_task_id = os.environ.get("SWARM_PARENT_TASK_ID")
    repo_path = os.environ.get("SWARM_REPO_PATH")

    if not repo_path:
        print("Error: SWARM_REPO_PATH not found in environment.")
        sys.exit(1)

    state = SwarmState()
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
