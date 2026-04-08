"""Web scraper — extract clean text from any URL."""

from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_webpage(url: str, max_chars: int = 5_000) -> str:
    """
    Extract readable text from a webpage.

    Args:
        url:       Full URL to scrape.
        max_chars: Maximum characters to return (default 5 000).

    Returns:
        Page title + main text, or an error message.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return "Error: invalid URL — provide a full URL like https://example.com"

    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.Timeout:
        return "Error: request timed out."
    except requests.RequestException as exc:
        return f"Error fetching page: {exc}"

    soup = BeautifulSoup(resp.content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = soup.find("title")
    title_text = f"Title: {title.get_text(strip=True)}\n\n" if title else ""

    lines = [ln.strip() for ln in soup.get_text(separator="\n").splitlines() if ln.strip()]
    text = "\n".join(lines)

    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n[truncated — total {len(text)} chars]"

    return title_text + text
