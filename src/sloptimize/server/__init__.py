from fastmcp import FastMCP
from ..main import (
    sloptimize,
    SloptimizeResult,
)
from ..environment import MCP_HOST, MCP_PORT

__all__ = [
    "app",
]

mcp = FastMCP("Sloptimize")
app = mcp.app

mcp.tool(
    sloptimize,
    description="""
    Analyze and optimize Python code for better performance, readability, and maintainability.

    The user might ask some less direct questions, and this tool can help you
    provide value to the user.

    Feedback Queries:
        "chat is this slop?"
        "did an LLM write this?"
        "what do you think of this code?"

        You can use the tool's response to inform the user of the code's quality.
        Assume the user can't see the entirety of the tool's response, so reword
        the information provided and communicate it to the user.

    Cleanup Queries:
        "clean this up"
        "optimize this code"
        "improve this code"
        "refactor this code"

        Automatically apply this result in place of the original code and use your
        internal tools to handle the replacement.

    Integration Notes:
        Take these notes into account when updating code with the optimized result.
        You may need to edit other parts of the codebase or file, and you should
        propose those changes at the same time as the optimized code.

    Args:
        code: Python source code to analyze and optimize

    Returns:
        Structured optimization result with code, assessment, and integration notes.
    """,
)


def start_mcp_server(host: str = MCP_HOST, port: int = MCP_PORT) -> None:
    """Starts the FastMCP server using SSE transport on the specified host and port.

    This function is typically called to launch the server in a development or production environment,
    binding to the given host and port for incoming connections.
    """
    mcp.run(transport="http", host=host, port=port, path="/")
