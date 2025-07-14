#!/usr/bin/env python3
"""
Simple worker daemon runner for systemd
"""
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / '..' / 'src'))

from sloptimize.worker.daemon import WorkerDaemon

if __name__ == "__main__":
    daemon = WorkerDaemon()
    daemon.run()