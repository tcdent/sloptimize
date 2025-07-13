"""
Utility functions for sloptimize
"""

import json
from typing import Any
from rich.console import Console
from rich.syntax import Syntax
from pydantic import BaseModel

console = Console()


def print_sloptimize_result(result) -> None:
    """
    Print SloptimizeResult with code preview and analysis

    Args:
        result: SloptimizeResult object from sloptimize function
    """
    # Import here to avoid circular imports
    from .main import SloptimizeResult

    if not isinstance(result, SloptimizeResult):
        raise TypeError(f"Expected SloptimizeResult, got {type(result)}")

    # Show optimized code first
    print_code(result.source_code)

    # Show structured analysis
    analysis_data = {
        "assessment": {
            "score": result.assessment.score,
            "metrics": result.assessment.metrics,
            "recommendations": result.assessment.recommendations,
        },
        "integration_considerations": result.integration_considerations,
    }

    json_str = json.dumps(analysis_data, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    console.print(syntax)


def print_json(data: Any) -> None:
    """
    Pretty-print JSON-like data with syntax highlighting using Rich.

    This utility function converts various data types to a formatted JSON string
    and displays it in the console with syntax highlighting. Useful for debugging
    or logging structured data in a readable format.

    Args:
        data: The data to print, which can be a dict, Pydantic BaseModel, JSON string,
              or other serializable object.
    """
    if isinstance(data, BaseModel):
        json_str = data.model_dump_json(indent=2)
    elif isinstance(data, dict):
        json_str = json.dumps(data, indent=2)
    elif isinstance(data, str):
        try:
            parsed = json.loads(data)
            json_str = json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            json_str = data
    else:
        json_str = json.dumps(data, indent=2, default=str)

    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    console.print(syntax)


def print_code(code: str, language: str = "python") -> None:
    """
    Print code with syntax highlighting

    Args:
        code: Source code to display
        language: Programming language for syntax highlighting
    """
    # Clean up the code - convert escaped newlines to actual newlines
    cleaned_code = code.replace("\\n", "\n").strip()

    # Create syntax highlighted code
    syntax = Syntax(
        cleaned_code, language, theme="monokai", line_numbers=False, word_wrap=True
    )

    console.print(syntax)
