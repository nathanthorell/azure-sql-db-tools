# Azure SQL DB Tools

A modern CLI tool for querying Azure SQL Database logs and diagnostics from Log Analytics workspaces. Provides terminal-based reporting as an alternative to the Azure Portal interface.

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Azure CLI (optional, for authentication)

### Initial Setup

1. Clone the repository:

   ```shell
   git clone <repository-url>
   cd azure-sql-db-tools
   ```

2. Install dependencies:

   ```shell
   uv sync
   ```

3. Configure your workspace:

   ```shell
   cp config-example.toml config.toml
   # Edit config.toml with your Azure Log Analytics workspace ID
   ```

### Configuration

Edit `config.toml` to customize your settings:

```toml
[azure]
workspace_id = "your-log-analytics-workspace-id"

[defaults]
time_range_minutes = 10
slow_query_threshold_ms = 5000

[logging]
level = "INFO"
verbose = false
```

## Common Commands

### SQL Error Analysis

```shell
# View recent SQL errors (default: 50 minutes)
uv run db-errors

# View errors from specific time period
uv run db-errors 30
```

### Performance Analysis

```shell
# View slow queries (default: 5000ms threshold)
uv run db-slow-queries

# View slow queries with custom time and threshold
uv run db-slow-queries 30 10000
```

### Development Commands

```shell
# Type checking
uv run mypy src/

# Code formatting
uv run ruff format src/

# Linting
uv run ruff check src/
```

## Project Structure

```text
azure-sql-db-tools/
├── src/
│   └── azure_sql_db_tools/
│       ├── __init__.py
│       ├── __main__.py          # Main CLI entry point
│       ├── cli.py               # Individual command entry points
│       ├── config.py            # Configuration management
│       ├── logs_client.py       # Azure Log Analytics client
│       └── rich_utils.py        # Terminal formatting utilities
├── config-example.toml          # Configuration template
├── config.toml                  # Configuration file (gitignored)
├── pyproject.toml              # Project dependencies and settings
└── README.md
```

## Authentication

The tool supports multiple authentication methods (in order of precedence):

1. **Environment Variables**: Azure service principal credentials
2. **Azure CLI**: `az login` authentication
3. **Interactive Browser**: Automatic browser-based login as fallback

For interactive authentication, the tool will automatically open your browser when needed.
