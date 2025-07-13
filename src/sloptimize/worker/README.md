# Sloptimize Worker Daemon

Background worker process that handles Git repository cloning, file analysis, and sloptimize processing.

## Overview

The worker daemon continuously monitors the database for pending jobs, clones repositories, processes code files with sloptimize, and stores results. It operates independently from the API server.

## Development Deployment

### Prerequisites
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (includes git)
pip install -e ".[dev]"

# Ensure git is available
which git
```

### Running the Worker

#### Foreground Mode (Development)
```bash
# Start worker daemon in foreground
python -m sloptimize.worker.daemon start

# In another terminal, check status
python -m sloptimize.worker.daemon status

# Stop when done
python -m sloptimize.worker.daemon stop
```

#### Background Mode
```bash
# Start as daemon
python -m sloptimize.worker.daemon start

# Check if running
python -m sloptimize.worker.daemon status

# Stop daemon
python -m sloptimize.worker.daemon stop

# Restart daemon
python -m sloptimize.worker.daemon restart
```

### Testing Worker Functionality
```bash
# Submit a job via API (in another terminal)
curl -X POST "http://localhost:8000/process-repository" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/octocat/Hello-World.git"}'

# Monitor worker logs
tail -f /tmp/sloptimize-worker.log
```

## Production Deployment (Debian 12)

### Manual Setup

1. **System dependencies**
```bash
sudo apt-get update
sudo apt-get install -y git python3.12 python3.12-venv
```

2. **Application setup** (if not done for API)
```bash
sudo useradd -r -s /bin/bash -d /opt/sloptimize sloptimize
sudo mkdir -p /opt/sloptimize
sudo cp -r . /opt/sloptimize/
sudo chown -R sloptimize:sloptimize /opt/sloptimize
sudo -u sloptimize python3.12 -m venv /opt/sloptimize/.venv
sudo -u sloptimize /opt/sloptimize/.venv/bin/pip install -e "/opt/sloptimize[dev]"
```

3. **Environment configuration**
```bash
sudo -u sloptimize cp /opt/sloptimize/.env.example /opt/sloptimize/.env
sudo -u sloptimize nano /opt/sloptimize/.env
```

4. **Install systemd service**
```bash
sudo cp /opt/sloptimize/scripts/sloptimize-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sloptimize-worker
sudo systemctl start sloptimize-worker
```

### Automated Setup
```bash
# Run the deployment script (includes worker setup)
sudo ./scripts/deploy.sh
```

## Configuration

### Worker Settings
Edit `src/sloptimize/worker/daemon.py` to customize:

```python
class WorkerDaemon:
    def __init__(self, 
                 pid_file: str = "/tmp/sloptimize-worker.pid",
                 log_file: str = "/tmp/sloptimize-worker.log",
                 max_workers: int = 2):  # Adjust concurrency
```

### File Processing Settings
Edit `src/sloptimize/worker/main.py`:

```python
class RepositoryProcessor:
    def __init__(self, job_id: str, repo_url: str):
        # Supported file extensions
        self.supported_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', # Add more as needed
        }
        
    async def _process_files_async(self, code_files: List[Path]):
        semaphore = asyncio.Semaphore(5)  # Concurrent files per job
```

### Environment Variables
Required in `/opt/sloptimize/.env`:
```bash
OPENAI_API_KEY=your-openai-api-key
XAI_API_KEY=your-xai-api-key
LLM_PROVIDER=openai  # or 'grok'
```

## Service Management

### Manual Daemon Control
```bash
# Start daemon
python -m sloptimize.worker.daemon start

# Stop daemon
python -m sloptimize.worker.daemon stop

# Restart daemon
python -m sloptimize.worker.daemon restart

# Check status
python -m sloptimize.worker.daemon status
```

### Systemd Service Control
```bash
# Start/stop/restart
sudo systemctl start sloptimize-worker
sudo systemctl stop sloptimize-worker
sudo systemctl restart sloptimize-worker

# Enable/disable auto-start
sudo systemctl enable sloptimize-worker
sudo systemctl disable sloptimize-worker

# Check status
sudo systemctl status sloptimize-worker

# View logs
sudo journalctl -u sloptimize-worker -f
```

## Monitoring

### Log Files
```bash
# Worker daemon logs
tail -f /tmp/sloptimize-worker.log

# Systemd logs
sudo journalctl -u sloptimize-worker -f

# Check for specific job processing
grep "job_id_here" /tmp/sloptimize-worker.log
```

### Process Monitoring
```bash
# Check if daemon is running
ps aux | grep sloptimize

# Check worker processes
pgrep -f "sloptimize.worker"

# Monitor resource usage
htop -p $(pgrep -f "sloptimize.worker")
```

### Database Monitoring
```bash
# Check job queue
sudo -u sloptimize /opt/sloptimize/.venv/bin/python -c "
from sloptimize.database import Database
db = Database()
pending = db.get_jobs(db.JobStatus.PENDING)
processing = db.get_jobs(db.JobStatus.PROCESSING)
print(f'Pending: {len(pending)}, Processing: {len(processing)}')
"

# Check recent results
sudo -u sloptimize /opt/sloptimize/.venv/bin/python -c "
from sloptimize.database import Database
db = Database()
jobs = db.get_jobs()
for job in jobs[:5]:
    print(f'{job[\"id\"]}: {job[\"status\"]} - {job[\"processed_files\"]}/{job[\"total_files\"]} files')
"
```

## File Processing

### Supported File Types
The worker processes these file extensions:
- **Python**: `.py`
- **JavaScript/TypeScript**: `.js`, `.ts`, `.jsx`, `.tsx`
- **Java**: `.java`
- **C/C++**: `.c`, `.cpp`, `.h`, `.hpp`
- **Go**: `.go`
- **Rust**: `.rs`
- **PHP**: `.php`
- **Ruby**: `.rb`
- **Swift**: `.swift`
- **Kotlin**: `.kt`
- **Scala**: `.scala`
- **R**: `.r`
- **Objective-C**: `.m`
- **SQL**: `.sql`
- **C#**: `.cs`

### Ignored Directories
- `.git`, `node_modules`, `__pycache__`
- `venv`, `.venv`, `env`, `.env`
- `build`, `dist`, `target`, `bin`, `obj`
- `.idea`, `.vscode`

### File Size Limits
- Maximum file size: 1MB
- Files larger than 1MB are skipped
- Empty files (< 50 characters) are skipped

## Troubleshooting

### Common Issues

**Worker not starting**
```bash
# Check systemd service
sudo systemctl status sloptimize-worker

# Check manual start
python -m sloptimize.worker.daemon start

# Check logs for errors
tail -n 50 /tmp/sloptimize-worker.log
```

**Git clone failures**
```bash
# Test git access manually
git clone --depth 1 https://github.com/octocat/Hello-World.git /tmp/test-clone

# Check worker logs for specific errors
grep "Git clone failed" /tmp/sloptimize-worker.log
```

**Jobs stuck in processing**
```bash
# Check for hung processes
ps aux | grep sloptimize

# Restart worker to clear stuck jobs
sudo systemctl restart sloptimize-worker

# Check database for processing jobs
sudo -u sloptimize /opt/sloptimize/.venv/bin/python -c "
from sloptimize.database import Database
db = Database()
processing = db.get_jobs(db.JobStatus.PROCESSING)
for job in processing:
    print(f'Job {job[\"id\"]} started at {job[\"started_at\"]}')
"
```

**High CPU/Memory usage**
```bash
# Reduce max workers in daemon.py
# Edit max_workers parameter to lower value

# Reduce file concurrency in main.py
# Edit semaphore value in _process_files_async
```

**Permission issues**
```bash
# Fix ownership
sudo chown -R sloptimize:sloptimize /opt/sloptimize

# Fix tmp directory permissions
sudo chmod 755 /tmp
sudo chown sloptimize:sloptimize /tmp/sloptimize-worker.pid
```

### Debug Mode

Enable detailed logging by editing the worker daemon:
```python
# In src/sloptimize/worker/daemon.py
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Manual Job Processing

For debugging, you can process a job manually:
```bash
# Get a pending job ID from database
# Then run worker directly
python -m sloptimize.worker.main <job_id> <repo_url>
```