"""
Database operations for sloptimize API
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Database:
    def __init__(self, db_path: str = "sloptimize.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    repo_url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    total_files INTEGER DEFAULT 0,
                    processed_files INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_results (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    original_code TEXT NOT NULL,
                    optimized_code TEXT NOT NULL,
                    score REAL NOT NULL,
                    metrics TEXT NOT NULL,
                    integration_considerations TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs (id)
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_results_job_id ON file_results(job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_results_score ON file_results(score DESC)")
            
            conn.commit()
    
    def create_job(self, repo_url: str) -> str:
        """Create a new job and return its ID"""
        job_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO jobs (id, repo_url, status) VALUES (?, ?, ?)",
                (job_id, repo_url, JobStatus.PENDING)
            )
            conn.commit()
        
        return job_id
    
    def update_job_status(self, job_id: str, status: JobStatus, error_message: Optional[str] = None):
        """Update job status"""
        with sqlite3.connect(self.db_path) as conn:
            if status == JobStatus.PROCESSING:
                conn.execute(
                    "UPDATE jobs SET status = ?, started_at = ? WHERE id = ?",
                    (status, datetime.now(), job_id)
                )
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                conn.execute(
                    "UPDATE jobs SET status = ?, completed_at = ?, error_message = ? WHERE id = ?",
                    (status, datetime.now(), error_message, job_id)
                )
            else:
                conn.execute(
                    "UPDATE jobs SET status = ?, error_message = ? WHERE id = ?",
                    (status, error_message, job_id)
                )
            conn.commit()
    
    def update_job_progress(self, job_id: str, total_files: int, processed_files: int):
        """Update job progress"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE jobs SET total_files = ?, processed_files = ? WHERE id = ?",
                (total_files, processed_files, job_id)
            )
            conn.commit()
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_jobs(self, status: Optional[JobStatus] = None) -> List[Dict[str, Any]]:
        """Get all jobs, optionally filtered by status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if status:
                cursor = conn.execute("SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC", (status,))
            else:
                cursor = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def save_file_result(self, job_id: str, file_path: str, original_code: str, 
                        optimized_code: str, score: float, metrics: Dict[str, Any], 
                        integration_considerations: List[str]):
        """Save optimization result for a file"""
        result_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO file_results 
                (id, job_id, file_path, original_code, optimized_code, score, metrics, integration_considerations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result_id, job_id, file_path, original_code, optimized_code, score,
                json.dumps(metrics), json.dumps(integration_considerations)
            ))
            conn.commit()
        
        return result_id
    
    def get_job_results(self, job_id: str, order_by_score: bool = True) -> List[Dict[str, Any]]:
        """Get all results for a job, optionally ordered by score"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            order_clause = "ORDER BY score DESC" if order_by_score else "ORDER BY created_at"
            cursor = conn.execute(
                f"SELECT * FROM file_results WHERE job_id = ? {order_clause}",
                (job_id,)
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['metrics'] = json.loads(result['metrics'])
                result['integration_considerations'] = json.loads(result['integration_considerations'])
                results.append(result)
            return results
    
    def get_top_results(self, job_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top results by score for a job"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM file_results WHERE job_id = ? ORDER BY score DESC LIMIT ?",
                (job_id, limit)
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['metrics'] = json.loads(result['metrics'])
                result['integration_considerations'] = json.loads(result['integration_considerations'])
                results.append(result)
            return results