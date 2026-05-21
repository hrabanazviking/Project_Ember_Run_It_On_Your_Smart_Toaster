"""Verðandi Heartbeat CLI — invoke with `python3 -m heartbeat.cli`."""
from heartbeat.cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)