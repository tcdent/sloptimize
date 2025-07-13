"""
FastAPI application for sloptimize repository processing
"""

import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
import subprocess
import sys
from pathlib import Path

from ..database import Database, JobStatus as DbJobStatus

app = FastAPI(title="Sloptimize API", version="0.1.0")
db = Database()

class RepositoryRequest(BaseModel):
    repo_url: HttpUrl
    
class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    repo_url: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    total_files: int = 0
    processed_files: int = 0
    progress_percent: float = 0.0

class FileResult(BaseModel):
    id: str
    file_path: str
    score: float
    metrics: Dict[str, Any]
    integration_considerations: List[str]
    created_at: str

def run_worker_process(job_id: str, repo_url: str):
    """Start worker process detached from API"""
    worker_script = Path(__file__).parent.parent / "worker" / "main.py"
    subprocess.Popen([
        sys.executable, str(worker_script), job_id, repo_url
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@app.post("/process-repository", response_model=JobResponse)
async def process_repository(request: RepositoryRequest, background_tasks: BackgroundTasks):
    """Submit a repository for processing"""
    try:
        job_id = db.create_job(str(request.repo_url))
        
        # Start worker process in background
        background_tasks.add_task(run_worker_process, job_id, str(request.repo_url))
        
        return JobResponse(
            job_id=job_id,
            status="pending",
            message="Repository processing started"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

@app.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status and progress"""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    progress_percent = 0.0
    if job['total_files'] > 0:
        progress_percent = (job['processed_files'] / job['total_files']) * 100
    
    return JobStatusResponse(
        job_id=job['id'],
        repo_url=job['repo_url'],
        status=job['status'],
        created_at=job['created_at'],
        started_at=job['started_at'],
        completed_at=job['completed_at'],
        error_message=job['error_message'],
        total_files=job['total_files'],
        processed_files=job['processed_files'],
        progress_percent=progress_percent
    )

@app.get("/jobs/{job_id}/results", response_model=List[FileResult])
async def get_job_results(job_id: str, limit: Optional[int] = None, order_by_score: bool = True):
    """Get optimization results for a job"""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if limit:
        results = db.get_top_results(job_id, limit)
    else:
        results = db.get_job_results(job_id, order_by_score)
    
    return [
        FileResult(
            id=result['id'],
            file_path=result['file_path'],
            score=result['score'],
            metrics=result['metrics'],
            integration_considerations=result['integration_considerations'],
            created_at=result['created_at']
        )
        for result in results
    ]

@app.get("/jobs", response_model=List[JobStatusResponse])
async def get_jobs(status: Optional[str] = None):
    """Get all jobs, optionally filtered by status"""
    job_status = None
    if status:
        try:
            job_status = DbJobStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    jobs = db.get_jobs(job_status)
    return [
        JobStatusResponse(
            job_id=job['id'],
            repo_url=job['repo_url'],
            status=job['status'],
            created_at=job['created_at'],
            started_at=job['started_at'],
            completed_at=job['completed_at'],
            error_message=job['error_message'],
            total_files=job['total_files'],
            processed_files=job['processed_files'],
            progress_percent=(job['processed_files'] / job['total_files'] * 100) if job['total_files'] > 0 else 0.0
        )
        for job in jobs
    ]

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Sloptimize API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)