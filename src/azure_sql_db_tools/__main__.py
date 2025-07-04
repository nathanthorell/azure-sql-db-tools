#!/usr/bin/env python3
"""
Azure SQL DB Tools - Main CLI entry point
"""

import sys

from .config import get_config
from .logs_client import LogsClient
from .rich_utils import display_slow_queries, display_sql_errors


def main() -> None:
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python -m azure_sql_db_tools <command> [options]")
        print("Commands: errors, slow-queries")
        sys.exit(1)

    command = sys.argv[1]
    config = get_config()
    minutes = int(sys.argv[2]) if len(sys.argv) > 2 else config.default_time_range

    # Initialize the client
    client = LogsClient()

    if command == "errors":
        results = client.recent_errors(minutes)
        display_sql_errors(results, f"Recent SQL Errors (last {minutes} minutes)")

    elif command == "slow-queries":
        threshold = int(sys.argv[3]) if len(sys.argv) > 3 else config.slow_query_threshold
        results = client.slow_queries(minutes, threshold)
        display_slow_queries(results, f"Slow Queries (last {minutes} minutes, >{threshold}ms)")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
