"""
Environment variable handling for sloptimize
"""
import os

# Load from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip
    pass

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# XAI/Grok Configuration  
XAI_API_KEY = os.getenv("XAI_API_KEY")
XAI_BASE_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")

# Model Configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "o1-3")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4")

# Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# MCP Server Configuration
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))