"""Email tool — saves emails to outputs/ (simulation)."""

from __future__ import annotations

import os
from datetime import datetime


def send_email(
    to: str,
    subject: str,
    message: str,
    from_email: str = "agent@example.com",
) -> str:
    """
    Simulate sending an email by saving it to outputs/.

    Args:
        to:         Recipient address.
        subject:    Email subject.
        message:    Email body.
        from_email: Sender address.

    Returns:
        Confirmation string with the saved filename.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = (
        f"From: {from_email}\n"
        f"To: {to}\n"
        f"Subject: {subject}\n"
        f"Date: {timestamp}\n"
        f"\n{message}\n"
        f"\n---\nSent by ReAct Agent\n"
    )

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    filename = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(output_dir, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(content)
        return f"Email saved as outputs/{filename}  (To: {to}, Subject: {subject})"
    except OSError as exc:
        return f"Error saving email: {exc}"
