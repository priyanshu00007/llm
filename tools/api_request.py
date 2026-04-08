"""HTTP API request tool."""

from __future__ import annotations

import json

import requests


def make_api_request(input_str: str) -> str:
    """
    Make an HTTP request.

    Input format (pipe-separated):
        URL
        URL|METHOD
        URL|METHOD|{json_body}

    Args:
        input_str: Pipe-separated request spec.

    Returns:
        Status code + response body (JSON pretty-printed or plain text).
    """
    parts = input_str.split("|", 2)
    url = parts[0].strip()
    method = parts[1].strip().upper() if len(parts) > 1 else "GET"
    raw_body = parts[2].strip() if len(parts) > 2 else None

    headers = {
        "User-Agent": "ReActAgent/2.0",
        "Accept": "application/json",
    }

    json_body: dict | None = None
    if raw_body:
        try:
            json_body = json.loads(raw_body)
        except json.JSONDecodeError:
            return "Error: request body is not valid JSON."

    try:
        resp = requests.request(
            method,
            url,
            json=json_body,
            headers=headers,
            timeout=15,
        )
        result = f"Status: {resp.status_code}\n"
        try:
            result += "Response:\n" + json.dumps(resp.json(), indent=2)[:3000]
        except ValueError:
            result += "Response:\n" + resp.text[:3000]
        return result
    except requests.Timeout:
        return "Error: request timed out."
    except requests.RequestException as exc:
        return f"Error making request: {exc}"
