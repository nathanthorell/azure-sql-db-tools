"""
CLI command functions for individual script entry points
"""

import sys

from .config import get_config
from .logs_client import LogsClient
from .rich_utils import display_slow_queries, display_sql_errors


def errors() -> None:
    """Entry point for db-errors command"""
    config = get_config()
    minutes = int(sys.argv[1]) if len(sys.argv) > 1 else config.default_time_range
    client = LogsClient()
    results = client.recent_errors(minutes)
    display_sql_errors(results, f"Recent SQL Errors (last {minutes} minutes)")


def slow_queries() -> None:
    """Entry point for db-slow-queries command"""
    config = get_config()
    minutes = int(sys.argv[1]) if len(sys.argv) > 1 else config.default_time_range
    threshold = int(sys.argv[2]) if len(sys.argv) > 2 else config.slow_query_threshold
    client = LogsClient()
    results = client.slow_queries(minutes, threshold)
    display_slow_queries(results, f"Slow Queries (last {minutes} minutes, >{threshold}ms)")
