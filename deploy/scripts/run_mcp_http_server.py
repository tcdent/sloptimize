#!/usr/bin/env python3
"""
Executable script to run the Sloptimize MCP server over HTTP.
This script sets up the Python path to include the 'src' directory and starts the MCP server.
"""
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / '..' / 'src'))

from sloptimize.server import start_mcp_server

if __name__ == "__main__":
    print("Starting Sloptimize MCP server on HTTP...")
    start_mcp_server()