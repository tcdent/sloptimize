# Sloptimize API Server

FastAPI-based REST API for submitting Git repositories for code optimization analysis.

## Overview

The API server handles HTTP requests to submit repositories for processing and query results. It operates independently from the worker processes, allowing for scalable deployment.

## Development Deployment

### Prerequisites
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the Server
```bash
# Development server (auto-reload)
python -m sloptimize.api
```

The server will start on `http://localhost:8000`

### Testing
```bash
# Run the test script
python scripts/test_api.py

# Manual testing
curl -X POST "http://localhost:8000/process-repository" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/octocat/Hello-World.git"}'
```

## Production Deployment (Debian 12)

### Manual Setup

1. **Create application user and directory**
```bash
sudo useradd -r -s /bin/bash -d /opt/sloptimize sloptimize
sudo mkdir -p /opt/sloptimize
sudo chown sloptimize:sloptimize /opt/sloptimize
```

2. **Install system dependencies**
```bash
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv nginx
```

3. **Deploy application**
```bash
# Copy files to server
sudo cp -r . /opt/sloptimize/
sudo chown -R sloptimize:sloptimize /opt/sloptimize

# Set up virtual environment
sudo -u sloptimize python3.12 -m venv /opt/sloptimize/.venv
sudo -u sloptimize /opt/sloptimize/.venv/bin/pip install -e "/opt/sloptimize[dev]"
```

4. **Configure environment**
```bash
sudo -u sloptimize cp /opt/sloptimize/.env.example /opt/sloptimize/.env
sudo -u sloptimize nano /opt/sloptimize/.env
```

5. **Install systemd service**
```bash
sudo cp /opt/sloptimize/scripts/sloptimize-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sloptimize-api
sudo systemctl start sloptimize-api
```

6. **Configure nginx**
```bash
sudo cp /opt/sloptimize/scripts/nginx.conf /etc/nginx/sites-available/sloptimize
sudo ln -sf /etc/nginx/sites-available/sloptimize /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Automated Setup
```bash
# Run the deployment script
sudo ./scripts/deploy.sh
```

## Configuration

### Environment Variables
Required in `/opt/sloptimize/.env`:
```bash
OPENAI_API_KEY=your-openai-api-key
XAI_API_KEY=your-xai-api-key
LLM_PROVIDER=openai  # or 'grok'
```

### Server Settings
Edit `src/sloptimize/server.py` to customize:
- Host/port binding
- Number of uvicorn workers
- Log levels

### Nginx Configuration
The nginx config in `scripts/nginx.conf` includes:
- Reverse proxy to uvicorn
- Request timeout settings
- Security headers
- Gzip compression

## Service Management

### Systemd Commands
```bash
# Start/stop/restart
sudo systemctl start sloptimize-api
sudo systemctl stop sloptimize-api
sudo systemctl restart sloptimize-api

# Enable/disable auto-start
sudo systemctl enable sloptimize-api
sudo systemctl disable sloptimize-api

# Check status
sudo systemctl status sloptimize-api

# View logs
sudo journalctl -u sloptimize-api -f
```

### Health Checks
```bash
# API health check
curl http://localhost:8000/

# Service status
sudo systemctl is-active sloptimize-api
```

## API Endpoints

### Submit Repository
```bash
curl -X POST "http://localhost:8000/process-repository" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo.git"}'
```

### Check Job Status
```bash
curl "http://localhost:8000/jobs/{job_id}/status"
```

### Get Results
```bash
curl "http://localhost:8000/jobs/{job_id}/results?limit=10"
```

### List Jobs
```bash
curl "http://localhost:8000/jobs?status=completed"
```

## Monitoring

### Log Files
- Application logs: `sudo journalctl -u sloptimize-api`
- Nginx access logs: `/var/log/nginx/access.log`
- Nginx error logs: `/var/log/nginx/error.log`

### Performance Monitoring
```bash
# Check process status
ps aux | grep sloptimize

# Monitor resource usage
htop -p $(pgrep -f "sloptimize.server")

# Check database size
ls -lh /opt/sloptimize/sloptimize.db
```

## Troubleshooting

### Common Issues

**Port already in use**
```bash
sudo lsof -i :8000
sudo systemctl stop sloptimize-api
```

**Permission denied**
```bash
sudo chown -R sloptimize:sloptimize /opt/sloptimize
sudo chmod +x /opt/sloptimize/.venv/bin/python
```

**Environment variables not loaded**
```bash
sudo -u sloptimize cat /opt/sloptimize/.env
# Verify API keys are set correctly
```

**Database connection issues**
```bash
sudo -u sloptimize /opt/sloptimize/.venv/bin/python -c "
from sloptimize.database import Database
db = Database()
print('Database connection OK')
"
```

### Debug Mode
For detailed debugging, edit the systemd service:
```bash
sudo systemctl edit sloptimize-api
```

Add:
```ini
[Service]
Environment=PYTHONPATH=/opt/sloptimize/src
Environment=DEBUG=1
```

Then restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart sloptimize-api
```