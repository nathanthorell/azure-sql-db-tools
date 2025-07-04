"""
Rich formatting utilities for Azure SQL DB Tools
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple

from rich.console import Console
from rich.table import Table
from rich.text import Text

# Define a type for table column justification
JustifyType = Literal["left", "center", "right"]

# Create a console for rich output
console = Console()

# Color scheme for different severity levels and data types
COLORS = {
    "error": "bright_red",
    "warning": "yellow",
    "success": "green",
    "info": "bright_blue",
    "header": "bold cyan",
    "timestamp": "bright_black",
    "database": "bright_green",
    "user": "bright_magenta",
    "statement": "white",
}


def create_table(
    title: Optional[str] = None,
    columns: Optional[List[str]] = None,
    padding: Tuple[int, int, int, int] = (0, 1, 0, 1),
) -> Table:
    """Create a standardized Rich table with consistent formatting.

    Args:
        title: Optional title for the table
        columns: List of column names
        padding: Tuple of padding values (top, right, bottom, left)

    Returns:
        A configured Rich Table object
    """
    table = Table(
        title=title,
        show_header=columns is not None,
        header_style=COLORS["header"],
        padding=padding,
        title_style=COLORS["header"],
    )

    # Add columns if provided
    if columns:
        for col in columns:
            table.add_column(col, justify="left")

    return table


def parse_additional_info(additional_info: str) -> Dict[str, str]:
    """Parse XML from additional_information_s field to extract error details.

    Args:
        additional_info: XML string from additional_information_s field

    Returns:
        Dictionary with parsed error information
    """
    if not additional_info or not additional_info.strip():
        return {}

    try:
        # Clean up the XML - sometimes it has extra characters
        xml_content = additional_info.strip()
        if not xml_content.startswith("<"):
            return {"raw": additional_info}

        root = ET.fromstring(xml_content)
        parsed = {}

        # Extract common error fields
        for elem in root.iter():
            if elem.text and elem.text.strip():
                parsed[elem.tag] = elem.text.strip()

        return parsed
    except ET.ParseError:
        return {"raw": additional_info}


def format_timestamp(timestamp: Any) -> Text:
    """Format timestamp with color coding.

    Args:
        timestamp: Timestamp value from query result

    Returns:
        Formatted Rich Text object
    """
    if isinstance(timestamp, datetime):
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    else:
        time_str = str(timestamp)

    return Text(time_str, style=COLORS["timestamp"])


def format_database_name(db_name: Any) -> Text:
    """Format database name with color coding.

    Args:
        db_name: Database name from query result

    Returns:
        Formatted Rich Text object
    """
    return Text(str(db_name) if db_name else "N/A", style=COLORS["database"])


def format_statement(statement: Any, max_length: int = 100) -> Text:
    """Format SQL statement with truncation and color coding.

    Args:
        statement: SQL statement from query result
        max_length: Maximum length before truncation

    Returns:
        Formatted Rich Text object
    """
    if not statement:
        return Text("N/A", style=COLORS["statement"])

    stmt_str = str(statement).strip()
    if len(stmt_str) > max_length:
        stmt_str = stmt_str[: max_length - 3] + "..."

    return Text(stmt_str, style=COLORS["statement"])


def display_sql_errors(results: Optional[List[Any]], title: str) -> None:
    """Display SQL error results in a formatted table.

    Args:
        results: Query results from LogsClient
        title: Title for the output
    """
    if not results:
        console.print(f"\n[{COLORS['info']}]{title}: No results found[/]")
        return

    table = create_table(
        title=title, columns=["Time", "Database", "User", "Action", "Statement", "Error Details"]
    )

    # Set column alignments
    table.columns[0].justify = "left"  # Time
    table.columns[1].justify = "left"  # Database
    table.columns[2].justify = "left"  # User
    table.columns[3].justify = "left"  # Action
    table.columns[4].justify = "left"  # Statement
    table.columns[5].justify = "left"  # Error Details

    for row in results:
        # Extract fields from the row (order matches the KQL query projection)
        time_generated = row[0] if len(row) > 0 else None
        database_name = row[1] if len(row) > 1 else None
        statement = row[2] if len(row) > 2 else None
        user_principal = row[3] if len(row) > 3 else None
        action_name = row[4] if len(row) > 4 else None
        additional_info = row[5] if len(row) > 5 else None

        # Parse additional information for error details
        error_info = parse_additional_info(str(additional_info)) if additional_info else {}
        error_details = error_info.get("error_message", error_info.get("raw", "Unknown error"))

        table.add_row(
            format_timestamp(time_generated),
            format_database_name(database_name),
            Text(str(user_principal) if user_principal else "N/A", style=COLORS["user"]),
            Text(str(action_name) if action_name else "N/A", style=COLORS["warning"]),
            format_statement(statement, 80),
            Text(
                str(error_details)[:100] + "..."
                if len(str(error_details)) > 100
                else str(error_details),
                style=COLORS["error"],
            ),
        )

    console.print(table)


def display_connection_issues(results: Optional[List[Any]], title: str) -> None:
    """Display connection issue results in a formatted table.

    Args:
        results: Query results from LogsClient
        title: Title for the output
    """
    if not results:
        console.print(f"\n[{COLORS['info']}]{title}: No results found[/]")
        return

    table = create_table(title=title, columns=["Time", "Principal", "Client IP", "Status"])

    for row in results:
        time_generated = row[0] if len(row) > 0 else None
        principal = row[1] if len(row) > 1 else None
        client_ip = row[2] if len(row) > 2 else None
        succeeded = row[3] if len(row) > 3 else None

        # Color code the status
        status_text = "SUCCESS" if str(succeeded).lower() == "true" else "FAILED"
        status_color = COLORS["success"] if str(succeeded).lower() == "true" else COLORS["error"]

        table.add_row(
            format_timestamp(time_generated),
            Text(str(principal) if principal else "N/A", style=COLORS["user"]),
            Text(str(client_ip) if client_ip else "N/A", style=COLORS["info"]),
            Text(status_text, style=status_color),
        )

    console.print(table)


def display_slow_queries(results: Optional[List[Any]], title: str) -> None:
    """Display slow query results in a formatted table.

    Args:
        results: Query results from LogsClient
        title: Title for the output
    """
    if not results:
        console.print(f"\n[{COLORS['info']}]{title}: No results found[/]")
        return

    table = create_table(
        title=title, columns=["Time", "Duration (ms)", "Statement", "Database", "User"]
    )

    # Set column alignments
    table.columns[1].justify = "right"  # Duration

    for row in results:
        # Extract fields from the row (order matches the KQL query projection)
        time_generated = row[0] if len(row) > 0 else None
        statement = row[1] if len(row) > 1 else None
        duration = row[2] if len(row) > 2 else None
        database_name = row[3] if len(row) > 3 else None
        user_principal = row[4] if len(row) > 4 else None

        # Color code duration based on severity
        duration_val = (
            float(duration) if duration and str(duration).replace(".", "").isdigit() else 0
        )
        if duration_val > 30000:  # 30+ seconds
            duration_color = COLORS["error"]
        elif duration_val > 10000:  # 10+ seconds
            duration_color = COLORS["warning"]
        else:
            duration_color = COLORS["info"]

        table.add_row(
            format_timestamp(time_generated),
            Text(f"{duration_val:,.0f}", style=duration_color),
            format_statement(statement, 100),
            format_database_name(database_name),
            Text(str(user_principal) if user_principal else "N/A", style=COLORS["user"]),
        )

    console.print(table)
