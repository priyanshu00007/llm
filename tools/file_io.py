"""File I/O tools — read and write files in outputs/ and data/."""

from __future__ import annotations

import os


def _outputs_dir() -> str:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    os.makedirs(path, exist_ok=True)
    return path


def _base_dir() -> str:
    return os.path.dirname(os.path.dirname(__file__))


def write_file(data: str, filename: str = "output.txt") -> str:
    """
    Write text to a file in outputs/.

    The tool also accepts the combined 'content|filename' format used by the agent.

    Args:
        data:     Content to write (or 'content|filename').
        filename: Target filename (default: output.txt).

    Returns:
        Confirmation with the saved path.
    """
    # Support 'content|filename' format
    if "|" in data and filename == "output.txt":
        parts = data.split("|", 1)
        data, filename = parts[0], parts[1].strip()

    filename = os.path.basename(filename)  # prevent path traversal
    filepath = os.path.join(_outputs_dir(), filename)

    try:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(str(data))
        return f"Saved to outputs/{filename}"
    except OSError as exc:
        return f"Error writing file: {exc}"


def read_file(filename: str) -> str:
    """
    Read a file from outputs/ or data/.

    Args:
        filename: File name (not a full path).

    Returns:
        File contents (truncated at 8 000 chars) or an error message.
    """
    filename = os.path.basename(filename)
    base = _base_dir()
    candidates = [
        os.path.join(base, "outputs", filename),
        os.path.join(base, "data", filename),
        os.path.join(base, filename),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                if len(content) > 8_000:
                    content = content[:8_000] + "\n… [truncated]"
                return content
            except OSError as exc:
                return f"Error reading file: {exc}"
    return f"File '{filename}' not found in outputs/ or data/."


def list_files(directory: str = "outputs") -> str:
    """List files in outputs/ or data/."""
    target = os.path.join(_base_dir(), directory)
    if not os.path.isdir(target):
        return f"Directory '{directory}' does not exist."
    files = sorted(os.listdir(target))
    if not files:
        return f"No files in {directory}/."
    return f"Files in {directory}/:\n" + "\n".join(f"  {f}" for f in files)
