"""
Azure SQL DB Tools - CLI for querying Azure SQL Database logs from Log Analytics
"""

from .__main__ import main
from .logs_client import LogsClient

__version__ = "0.1.0"
__all__ = ["LogsClient", "main"]
