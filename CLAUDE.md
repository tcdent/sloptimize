# Claude Development Notes

## Environment Setup

### Virtual Environment
**Always activate the virtual environment before running any Python commands:**

```bash
source .venv/bin/activate
```

### Environment Variables
1. Copy `.env.example` to `.env`
2. Fill in your API keys:
   - `OPENAI_API_KEY`: Your OpenAI API key for O1-3 access
   - `XAI_API_KEY`: Your XAI API key for Grok-4 access

## Running Tests

### Install Dependencies
```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run Tests with Pytest
```bash
source .venv/bin/activate
pytest tests/
```

### Run Specific Test
```bash
source .venv/bin/activate
pytest tests/test_sloptimize.py -v
```

## Development Dependencies

The following dev dependencies are available in the `[project.optional-dependencies]` section:
- `pytest>=7.0.0`: Testing framework
- `pytest-cov>=4.0.0`: Coverage reporting

Install with: `pip install -e ".[dev]"`

## Project Structure

- `src/main.py`: Core sloptimize functionality
- `src/environment.py`: Environment variable handling
- `src/llm.py`: LLM clients (OpenAI O1-3, Grok-4)
- `src/mcp/`: MCP server implementation
- `tests/`: Unit tests