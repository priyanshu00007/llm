"""Date and time utilities."""

from __future__ import annotations

from datetime import datetime, timezone


def get_current_time(_: str = "") -> str:
    """Return the current local date and time as YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_date(_: str = "") -> str:
    """Return today's date as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


def get_utc_time(_: str = "") -> str:
    """Return the current UTC time as YYYY-MM-DD HH:MM:SS UTC."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def format_date(
    date_string: str,
    input_format: str = "%Y-%m-%d",
    output_format: str = "%B %d, %Y",
) -> str:
    """Reformat a date string from one format to another."""
    try:
        return datetime.strptime(date_string, input_format).strftime(output_format)
    except ValueError as exc:
        return f"Error formatting date: {exc}"
