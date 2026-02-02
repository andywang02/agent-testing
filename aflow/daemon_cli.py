from aflow.state import AflowState
from aflow.runner import AflowDaemon
import sys

def main():
    state = AflowState()
    daemon = AflowDaemon(state)
    print("Aflow Daemon starting...")
    try:
        daemon.start()
    except KeyboardInterrupt:
        print("\nAflow Daemon stopping...")
        daemon.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
