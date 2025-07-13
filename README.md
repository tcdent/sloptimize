# Sloptimize

Code analysis and optimization tool powered by AI.

## Installation

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [Claude Code](https://claude.ai/code) CLI

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sloptimize
   ```

2. Create and activate virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv add mcp
   pip install -e ".[dev]"
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # OPENAI_API_KEY=your_openai_key
   # XAI_API_KEY=your_xai_key
   ```

### Claude Code Integration

To use Sloptimize as an MCP server with Claude Code:

1. Add the MCP server to Claude Code:
   ```bash
   claude mcp add sloptimize uv run python scripts/run_mcp_server.py
   ```

2. The `sloptimize` tool will now be available in your Claude Code sessions for analyzing and optimizing code.

### Usage

#### Direct Usage
```bash
source .venv/bin/activate
python -m src.main "your code here"
```

#### Through Claude Code
Once the MCP server is configured, you can use the `sloptimize` tool directly in Claude Code conversations to analyze and optimize code snippets.

### Development

Run tests:
```bash
source .venv/bin/activate
pytest tests/
```

Run specific test:
```bash
source .venv/bin/activate
pytest tests/test_sloptimize.py -v
```