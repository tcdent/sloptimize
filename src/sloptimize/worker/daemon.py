"""
Daemon wrapper for the sloptimize worker process
"""

import sys
import os
import signal
import time
import logging
import multiprocessing
from pathlib import Path
from queue import Queue, Empty
import json
import daemon
import daemon.pidfile
from typing import Optional

from ..database import Database, JobStatus


class WorkerDaemon:
    """Daemon that manages worker processes for pending jobs"""
    
    def __init__(self, 
                 pid_file: str = "/tmp/sloptimize-worker.pid",
                 log_file: str = "/tmp/sloptimize-worker.log",
                 max_workers: int = 2):
        self.pid_file = pid_file
        self.log_file = log_file
        self.max_workers = max_workers
        self.db = Database()
        self.workers = {}
        self.shutdown_requested = False
        
        # Setup logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown_requested = True
    
    def start_worker_process(self, job_id: str, repo_url: str) -> multiprocessing.Process:
        """Start a worker process for a job"""
        from .main import RepositoryProcessor
        
        def worker_target():
            import asyncio
            processor = RepositoryProcessor(job_id, repo_url)
            asyncio.run(processor.process())
        
        process = multiprocessing.Process(target=worker_target)
        process.start()
        self.logger.info(f"Started worker process {process.pid} for job {job_id}")
        return process
    
    def cleanup_finished_workers(self):
        """Clean up finished worker processes"""
        finished_jobs = []
        for job_id, process in self.workers.items():
            if not process.is_alive():
                process.join()
                finished_jobs.append(job_id)
                self.logger.info(f"Worker process for job {job_id} finished")
        
        for job_id in finished_jobs:
            del self.workers[job_id]
    
    def check_for_pending_jobs(self):
        """Check for pending jobs and start workers if available"""
        if len(self.workers) >= self.max_workers:
            return
        
        pending_jobs = self.db.get_jobs(JobStatus.PENDING)
        
        for job in pending_jobs:
            if len(self.workers) >= self.max_workers:
                break
            
            job_id = job['id']
            repo_url = job['repo_url']
            
            # Start worker for this job
            process = self.start_worker_process(job_id, repo_url)
            self.workers[job_id] = process
    
    def run(self):
        """Main daemon loop"""
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.logger.info("Worker daemon starting...")
        
        while not self.shutdown_requested:
            try:
                # Clean up finished workers
                self.cleanup_finished_workers()
                
                # Check for new pending jobs
                self.check_for_pending_jobs()
                
                # Sleep before next check
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error in daemon loop: {e}")
                time.sleep(10)
        
        # Shutdown: wait for all workers to finish
        self.logger.info("Shutting down, waiting for workers to finish...")
        for job_id, process in self.workers.items():
            process.join(timeout=30)
            if process.is_alive():
                self.logger.warning(f"Force killing worker for job {job_id}")
                process.terminate()
                process.join()
        
        self.logger.info("Worker daemon stopped")
    
    def start_daemon(self):
        """Start the daemon"""
        try:
            with daemon.DaemonContext(
                pidfile=daemon.pidfile.PIDLockFile(self.pid_file),
                stdout=open(self.log_file, 'a'),
                stderr=open(self.log_file, 'a'),
                signal_map={
                    signal.SIGTERM: self.signal_handler,
                    signal.SIGINT: self.signal_handler,
                }
            ):
                self.run()
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {e}")
            raise
    
    def stop_daemon(self):
        """Stop the daemon"""
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            print(f"Sent SIGTERM to daemon process {pid}")
            
            # Wait for process to stop
            for _ in range(30):
                try:
                    os.kill(pid, 0)
                    time.sleep(1)
                except OSError:
                    break
            else:
                print("Daemon didn't stop gracefully, sending SIGKILL")
                os.kill(pid, signal.SIGKILL)
            
            # Remove pid file
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                
        except FileNotFoundError:
            print("Daemon not running (no pid file)")
        except ProcessLookupError:
            print("Daemon not running (process not found)")
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
        except Exception as e:
            print(f"Error stopping daemon: {e}")
    
    def status(self):
        """Check daemon status"""
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, 0)
                print(f"Daemon is running (PID: {pid})")
                
                # Show worker status
                active_jobs = len(self.workers) if hasattr(self, 'workers') else 0
                print(f"Active workers: {active_jobs}/{self.max_workers}")
                
            except OSError:
                print("Daemon is not running (stale pid file)")
                os.remove(self.pid_file)
                
        except FileNotFoundError:
            print("Daemon is not running")


def main():
    """CLI entry point for daemon management"""
    if len(sys.argv) < 2:
        print("Usage: python -m sloptimize.worker.daemon {start|stop|restart|status}")
        sys.exit(1)
    
    command = sys.argv[1]
    daemon = WorkerDaemon()
    
    if command == "start":
        print("Starting worker daemon...")
        daemon.start_daemon()
    elif command == "stop":
        print("Stopping worker daemon...")
        daemon.stop_daemon()
    elif command == "restart":
        print("Restarting worker daemon...")
        daemon.stop_daemon()
        time.sleep(2)
        daemon.start_daemon()
    elif command == "status":
        daemon.status()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()