# Sloptimize Deployment Guide

This directory contains all the configuration files and documentation for deploying Sloptimize services.

## Services Overview

Sloptimize consists of three main services running on different domains:

- **Frontend** (sloptimize.ai, www.sloptimize.ai) - React landing page
- **MCP Server** (mcp.sloptimize.ai) - Model Context Protocol server for code optimization
- **API Server** (api.sloptimize.ai) - FastAPI backend for repository processing

## Service URLs

| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| Frontend | https://sloptimize.ai | 443 | React landing page with installation instructions |
| MCP Server | https://mcp.sloptimize.ai | 9000 | Code optimization via MCP protocol |
| API Server | https://api.sloptimize.ai | 9090 | Repository processing API |

## Configuration Files

### Nginx (`nginx/`)
- `sloptimize.ai` - Main website and www redirect configuration
- `mcp.sloptimize.ai` - MCP server proxy with 5-minute timeouts
- `api.sloptimize.ai` - API server proxy with CORS headers

### Systemd Services (`systemd/`)
- `sloptimize-mcp.service` - MCP server daemon
- `sloptimize-api.service` - FastAPI server daemon  
- `sloptimize-worker.service` - Background worker daemon (not currently enabled)

### Scripts (`scripts/`)
- `run_mcp_http_server.py` - MCP server entry point
- `run_worker_daemon.py` - Worker daemon wrapper

## Interacting with Services

### MCP Server (mcp.sloptimize.ai)

**Purpose**: Code optimization via Model Context Protocol

**Integration with Claude Code**:
```bash
claude mcp add --transport http sloptimize https://mcp.sloptimize.ai
```

**Integration with Cursor**:
```json
{
  "mcpServers": {
    "sloptimize": {
      "transport": {
        "type": "http",
        "url": "https://mcp.sloptimize.ai"
      }
    }
  }
}
```

**Direct HTTP Testing**:
```bash
# Health check
curl -I https://mcp.sloptimize.ai

# Expected: HTTP/2 405 with mcp-session-id header
```

**Features**:
- Powered by Grok-4 LLM
- 5-minute request timeout
- Structured code analysis and optimization
- Integration considerations and metrics

### API Server (api.sloptimize.ai)

**Purpose**: Repository processing and job management

**Health Check**:
```bash
curl https://api.sloptimize.ai
# Returns: {"message":"Sloptimize API is running"}
```

**Submit Repository for Processing**:
```bash
curl -X POST https://api.sloptimize.ai/process-repository \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo"}'

# Returns: {"job_id": "uuid", "status": "pending", "message": "Repository processing started"}
```

**Check Job Status**:
```bash
curl https://api.sloptimize.ai/jobs/{job_id}/status
```

**Get Job Results**:
```bash
curl https://api.sloptimize.ai/jobs/{job_id}/results
```

**List All Jobs**:
```bash
curl https://api.sloptimize.ai/jobs
curl https://api.sloptimize.ai/jobs?status=completed
```

### Frontend (sloptimize.ai)

**Purpose**: Landing page with installation instructions

**Features**:
- Installation guide for Claude Code and Cursor
- MCP configuration examples
- Code examples and feature showcase
- Responsive React design

## Service Management

### Checking Service Status
```bash
sudo systemctl status sloptimize-mcp
sudo systemctl status sloptimize-api
sudo systemctl status sloptimize-worker
```

### Restarting Services
```bash
sudo systemctl restart sloptimize-mcp
sudo systemctl restart sloptimize-api
sudo systemctl restart sloptimize-worker
```

### Viewing Logs
```bash
# Service logs
sudo journalctl -u sloptimize-mcp -f
sudo journalctl -u sloptimize-api -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Updating Code
```bash
cd /home/admin/sloptimize
git pull origin main
sudo systemctl restart sloptimize-mcp sloptimize-api
```

### Updating Frontend
```bash
cd /home/admin/sloptimize/ui
npm run build
# No restart needed - symlinked to nginx
```

## Environment Configuration

Services read environment variables from `/home/admin/sloptimize/.env`:

```bash
# Required
LLM_PROVIDER=grok
XAI_API_KEY="your_xai_api_key"
OPENAI_API_KEY="your_openai_api_key"
WANDB_API_KEY="your_wandb_api_key"

# Optional - defaults provided
MCP_HOST=0.0.0.0
MCP_PORT=9000
API_HOST=0.0.0.0
API_PORT=9090
```

## SSL Certificates

SSL certificates are managed by Let's Encrypt with auto-renewal:

```bash
# Check certificate status
sudo certbot certificates

# Manual renewal test
sudo certbot renew --dry-run
```

## Concurrency Notes

- **MCP Server**: Single-threaded, processes one request at a time
- **API Server**: Multi-threaded FastAPI with background task processing
- **Frontend**: Static files served by nginx

For high-traffic MCP usage, consider implementing async processing or multiple workers.

## Troubleshooting

### MCP Server Not Responding
1. Check service status: `sudo systemctl status sloptimize-mcp`
2. Check logs: `sudo journalctl -u sloptimize-mcp -n 50`
3. Verify environment: `sudo cat /home/admin/sloptimize/.env`
4. Test locally: `curl -I http://localhost:9000`

### API Server Errors
1. Check service status: `sudo systemctl status sloptimize-api`
2. Check database: `ls -la /home/admin/sloptimize/sloptimize.db`
3. Test health endpoint: `curl https://api.sloptimize.ai`

### Frontend Not Loading
1. Check nginx config: `sudo nginx -t`
2. Verify symlink: `ls -la /var/www/sloptimize`
3. Rebuild if needed: `cd /home/admin/sloptimize/ui && npm run build`

### SSL Issues
1. Check certificate expiry: `sudo certbot certificates`
2. Verify nginx SSL config in `/etc/nginx/sites-available/`
3. Test renewal: `sudo certbot renew --dry-run`