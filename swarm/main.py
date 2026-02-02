import argparse
import os
import sys
import subprocess
from swarm.state import SwarmState
from swarm.allocator import TaskAllocator
from swarm.session import SessionManager
from swarm.models import TaskStatus

def main():
    parser = argparse.ArgumentParser(description="Swarm: Parallel Claude Code Sessions")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Start
    start_parser = subparsers.add_parser("start", help="Start a new task")
    start_parser.add_argument("description", help="Task description")
    start_parser.add_argument("--name", help="Task name", default="Task")
    start_parser.add_argument("--repo", help="Repo path or URL", default=".")

    # List
    list_parser = subparsers.add_parser("list", help="List tasks and sessions")

    # Attach
    attach_parser = subparsers.add_parser("attach", help="Attach to a session")
    attach_parser.add_argument("session_id", help="Session ID (or prefix)")

    # Send
    send_parser = subparsers.add_parser("send", help="Send a message to a task")
    send_parser.add_argument("task_id", help="Task ID")
    send_parser.add_argument("message", help="Message content")

    # Resume
    resume_parser = subparsers.add_parser("resume", help="Resume a task with a message")
    resume_parser.add_argument("task_id", help="Task ID")
    resume_parser.add_argument("message", help="Message content")

    args = parser.parse_args()

    state = SwarmState()
    allocator = TaskAllocator(state)

    if args.command == "start":
        repo_path = os.path.abspath(args.repo) if os.path.exists(args.repo) else args.repo
        task = allocator.create_task(args.name, args.description, repo_path)
        print(f"Created task {task.id}: {task.name}")
        print(f"Run 'swarm-daemon' to process it.")

    elif args.command == "list":
        print(f"{'ID':<38} {'NAME':<20} {'STATUS':<10}")
        for task in state.tasks.values():
            print(f"{task.id:<38} {task.name:<20} {task.status.value:<10}")

        print("\nSessions:")
        print(f"{'ID':<38} {'TASK_ID':<38} {'TMUX':<15} {'STATUS':<10}")
        for session in state.sessions.values():
            print(f"{session.id:<38} {session.task_id:<38} {session.tmux_session_id:<15} {session.status.value:<10}")

    elif args.command == "attach":
        # Find session by ID or prefix
        session = None
        for s in state.sessions.values():
            if s.id.startswith(args.session_id) or s.tmux_session_id == args.session_id:
                session = s
                break

        if not session:
            print(f"Session {args.session_id} not found.")
            sys.exit(1)

        os.execvp("tmux", ["tmux", "attach-session", "-t", session.tmux_session_id])

    elif args.command == "send" or args.command == "resume":
        task_id = args.task_id
        # Allow prefix for task_id or match by name
        if task_id not in state.tasks:
            found = False
            for tid, t in state.tasks.items():
                if tid.startswith(task_id) or t.name == task_id:
                    task_id = tid
                    found = True
                    break
            if not found:
                print(f"Task {args.task_id} not found.")
                sys.exit(1)

        allocator.resume_task(task_id, args.message)
        print(f"Sent message to task {task_id}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
