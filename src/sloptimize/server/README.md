# Sloptimize MCP Server

This directory contains the Model Context Protocol (MCP) server implementation for Sloptimize.

## Overview

The MCP server exposes Sloptimize's code optimization functionality as an MCP tool that can be integrated with Claude Desktop, IDEs, and other MCP-compatible clients.

## Server Implementation

### FastMCP Server (`__init__.py`)

The server uses the official MCP Python SDK's FastMCP implementation:

```python
from mcp.server.fastmcp.server import FastMCP
```

#### Key Components:

1. **Tool Definition**: `sloptimize_code` tool that accepts Python code and returns optimized version with assessment
2. **Transport**: Server-Sent Events (SSE) transport for real-time communication
3. **Error Handling**: Graceful error handling for malformed requests and optimization failures

### Available Tools

#### `sloptimize_code`
- **Description**: Analyze and optimize Python code for better performance, readability, and maintainability
- **Input**: `code` (string) - Python source code to analyze and optimize
- **Output**: Formatted response containing:
  - Optimized code with syntax highlighting
  - Assessment score (1-5)
  - Integration considerations

## Running the Server

### Script Method
```bash
python scripts/run_mcp_http_server.py
```

### Direct Import
```python
from sloptimize.server import start_mcp_server
start_mcp_server()
```

### Default Configuration
- **Transport**: SSE (Server-Sent Events)
- **Port**: 8001 (when run via script)
- **Host**: 0.0.0.0

## MCP Protocol Endpoints

When running, the server exposes MCP protocol endpoints that handle:
- Tool discovery
- Tool execution
- Real-time communication via SSE

## Integration Notes

### Claude Desktop Integration
Add to Claude Desktop MCP settings:
```json
{
  "sloptimize": {
    "command": "python",
    "args": ["scripts/run_mcp_http_server.py"],
    "env": {
      "OPENAI_API_KEY": "your-key-here",
      "XAI_API_KEY": "your-key-here"
    }
  }
}
```

### API Client Integration
The server can be accessed programmatically by MCP clients that support SSE transport.

## Troubleshooting

### Common Issues

1. **404 Errors**: Ensure you're using the correct MCP Python SDK import path:
   ```python
   from mcp.server.fastmcp.server import FastMCP  # Correct
   from fastmcp import FastMCP  # Incorrect
   ```

2. **Import Errors**: Make sure the MCP Python SDK is installed:
   ```bash
   pip install mcp
   ```

3. **Connection Issues**: Verify the server is running on the expected port and that environment variables are set correctly.

### Server Status
- ✅ **Working**: MCP protocol endpoints via SSE transport
- ✅ **Working**: Tool discovery and execution
- ✅ **Working**: Error handling and graceful failures

## Dependencies

- `mcp` - Official MCP Python SDK
- Core sloptimize dependencies (see main project requirements)