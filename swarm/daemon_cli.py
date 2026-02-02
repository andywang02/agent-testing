from swarm.state import SwarmState
from swarm.runner import SwarmDaemon
import sys

def main():
    state = SwarmState()
    daemon = SwarmDaemon(state)
    print("Swarm Daemon starting...")
    try:
        daemon.start()
    except KeyboardInterrupt:
        print("\nSwarm Daemon stopping...")
        daemon.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
