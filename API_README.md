# Sloptimize Repository Processing API

A FastAPI-based service for processing Git repositories with sloptimize, featuring background workers and SQLite storage.

## Architecture

- **FastAPI Server**: Handles API requests and responses
- **Worker Daemon**: Processes repositories in the background
- **SQLite Database**: Stores job status and optimization results
- **Git Integration**: Clones and analyzes public repositories

## Quick Start

### Development

```bash
# Install dependencies
source .venv/bin/activate
pip install -e ".[dev]"

# Start the API server
python -m sloptimize.api

# Start the worker daemon (in another terminal)
python -m sloptimize.worker.daemon start

# Test the API
python scripts/test_api.py
```

### Production (Debian 12)

```bash
# Deploy the complete system
sudo ./scripts/deploy.sh

# Manage services
sudo systemctl status sloptimize-api
sudo systemctl status sloptimize-worker

# View logs
sudo journalctl -u sloptimize-api -f
sudo journalctl -u sloptimize-worker -f
```

## API Endpoints

### Submit Repository for Processing
```http
POST /process-repository
Content-Type: application/json

{
    "repo_url": "https://github.com/user/repo.git"
}
```

Response:
```json
{
    "job_id": "uuid-here",
    "status": "pending",
    "message": "Repository processing started"
}
```

### Get Job Status
```http
GET /jobs/{job_id}/status
```

Response:
```json
{
    "job_id": "uuid-here",
    "repo_url": "https://github.com/user/repo.git",
    "status": "processing",
    "created_at": "2024-01-01T00:00:00",
    "total_files": 50,
    "processed_files": 25,
    "progress_percent": 50.0
}
```

### Get Optimization Results
```http
GET /jobs/{job_id}/results?limit=10&order_by_score=true
```

Response:
```json
[
    {
        "id": "result-uuid",
        "file_path": "src/main.py",
        "score": 8.5,
        "metrics": {
            "complexity_improvement": "Reduced cyclomatic complexity",
            "readability_score": "Improved variable naming",
            "performance_gain": "Optimized loops"
        },
        "integration_considerations": [
            "Update import statements",
            "Method signature changed"
        ],
        "created_at": "2024-01-01T00:00:00"
    }
]
```

### List All Jobs
```http
GET /jobs?status=completed
```

## Database Schema

### Jobs Table
- `id`: Unique job identifier
- `repo_url`: Repository URL
- `status`: pending/processing/completed/failed
- `created_at`, `started_at`, `completed_at`: Timestamps
- `total_files`, `processed_files`: Progress tracking
- `error_message`: Error details if failed

### File Results Table
- `id`: Unique result identifier
- `job_id`: Foreign key to jobs table
- `file_path`: Relative path within repository
- `original_code`: Original file content
- `optimized_code`: Sloptimize output
- `score`: Optimization impact score
- `metrics`: JSON-encoded metrics
- `integration_considerations`: JSON-encoded list

## Worker Management

### Manual Control
```bash
# Start daemon
python -m sloptimize.worker.daemon start

# Stop daemon
python -m sloptimize.worker.daemon stop

# Check status
python -m sloptimize.worker.daemon status
```

### Systemd (Production)
```bash
# Start/stop services
sudo systemctl start sloptimize-worker
sudo systemctl stop sloptimize-worker

# Enable auto-start
sudo systemctl enable sloptimize-worker
```

## Configuration

### Environment Variables
Create `.env` file:
```bash
OPENAI_API_KEY=your-openai-key
XAI_API_KEY=your-xai-key
LLM_PROVIDER=openai  # or 'grok'
```

### Worker Settings
- Max concurrent workers: 2 (configurable in daemon.py)
- Supported file types: .py, .js, .ts, .java, .cpp, .go, etc.
- File size limit: 1MB per file
- Concurrency per job: 5 files at once

## Nginx Configuration

The system includes nginx configuration for:
- Reverse proxy to FastAPI server
- Static file serving
- Security headers
- Gzip compression
- Long-running request support

## Monitoring

### Logs
- API logs: `/var/log/sloptimize-api.log`
- Worker logs: `/tmp/sloptimize-worker.log`
- Nginx logs: `/var/log/nginx/access.log`

### Health Checks
- API health: `GET /`
- Service status: `systemctl status sloptimize-*`

## Security Considerations

- Repository cloning uses temporary directories
- Worker processes run with restricted permissions
- No shell injection vulnerabilities in git operations
- File size limits prevent resource exhaustion
- Systemd services run as dedicated user

## Troubleshooting

### Common Issues

1. **Worker not processing jobs**: Check daemon logs and restart service
2. **API not responding**: Verify uvicorn is running and port is available
3. **Git clone failures**: Ensure repository is public and accessible
4. **Database locked**: Check for concurrent access issues

### Debug Commands
```bash
# Check running processes
ps aux | grep sloptimize

# Test database connection
python -c "from sloptimize.database import Database; db = Database(); print(db.get_jobs())"

# Test git clone manually
git clone --depth 1 <repo_url> /tmp/test-clone
```