"""Database tool — safe SQLite query execution."""

from __future__ import annotations

import os
import sqlite3


def _resolve_db_path(db_path: str) -> str:
    """Resolve a relative db path against the project root."""
    if os.path.isabs(db_path):
        return db_path
    base = os.path.dirname(os.path.dirname(__file__))
    for candidate in (
        os.path.join(base, "data", db_path),
        os.path.join(base, db_path),
    ):
        if os.path.exists(candidate):
            return candidate
    return os.path.join(base, db_path)


def query_database(query: str, db_path: str = "database.db") -> str:
    """
    Execute a SQL query on a SQLite database.

    Args:
        query:   SQL statement to execute.
        db_path: Path to the SQLite file (default: database.db).

    Returns:
        Formatted results for SELECT, or row-count for DML statements.
    """
    # Basic SQL injection guard — block stacked statements
    stripped = query.strip().rstrip(";")
    if ";" in stripped:
        return "Error: only single SQL statements are allowed."

    try:
        path = _resolve_db_path(db_path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)

        upper = query.strip().upper()
        if upper.startswith(("SELECT", "PRAGMA", "WITH")):
            rows = cursor.fetchall()
            conn.close()
            if not rows:
                return "Query executed successfully. No rows returned."

            headers = list(rows[0].keys())
            col_widths = {
                col: max(len(col), max(len(str(row[col])) for row in rows[:50]))
                for col in headers
            }

            sep = "-+-".join("-" * col_widths[c] for c in headers)
            header_line = " | ".join(c.ljust(col_widths[c]) for c in headers)
            lines = [header_line, sep]
            for row in rows[:50]:
                lines.append(" | ".join(str(row[c]).ljust(col_widths[c]) for c in headers))
            if len(rows) > 50:
                lines.append(f"… and {len(rows) - 50} more rows")
            lines.append(f"\nTotal rows: {len(rows)}")
            return "\n".join(lines)
        else:
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return f"Query executed. Rows affected: {affected}"

    except sqlite3.Error as exc:
        return f"Database error: {exc}"
    except Exception as exc:
        return f"Error: {exc}"
