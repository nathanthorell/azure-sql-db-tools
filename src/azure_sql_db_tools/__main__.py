"""
Azure SQL DB Tools - Main CLI entry point
"""

from typing import Optional

import typer

from .config import get_config
from .logs_client import LogsClient
from .rich_utils import display_slow_queries, display_sql_errors

app = typer.Typer(name="azure-sql-db-tools", help="Azure SQL DB diagnostics CLI")


@app.command()
def errors(minutes: Optional[int] = typer.Argument(None, help="Time range in minutes")) -> None:
    """Show recent SQL errors from Log Analytics."""
    config = get_config()
    actual_minutes = minutes if minutes is not None else config.default_time_range

    client = LogsClient()
    results = client.recent_errors(actual_minutes)
    display_sql_errors(results, f"Recent SQL Errors (last {actual_minutes} minutes)")


@app.command()
def slow_queries(
    minutes: Optional[int] = typer.Argument(None, help="Time range in minutes"),
    threshold: Optional[int] = typer.Argument(None, help="Threshold in milliseconds"),
) -> None:
    """Show slow queries above threshold."""
    config = get_config()
    actual_minutes = minutes if minutes is not None else config.default_time_range
    actual_threshold = threshold if threshold is not None else config.slow_query_threshold

    client = LogsClient()
    results = client.slow_queries(actual_minutes, actual_threshold)
    display_slow_queries(
        results, f"Slow Queries (last {actual_minutes} minutes, >{actual_threshold}ms)"
    )


def main() -> None:
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
