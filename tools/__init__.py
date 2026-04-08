"""Tools module for ReAct Agent.

This module contains all the tools that can be used by the agent.
"""

from .calculator import calculator
from .email import send_email
from .weather import get_weather
from .file_io import write_file, read_file
from .datetime_tool import get_current_time
from .web_scraper import scrape_webpage
from .api_request import make_api_request
from .database import query_database
from .csv_analyzer import analyze_csv
from .web_crawler import (
    crawl_website,
    search_web,
    get_weather_no_api,
    get_latest_news,
    get_stock_price_no_api,
    extract_product_details,
    extract_faq_from_page,
)

__all__ = [
    "calculator",
    "send_email",
    "get_weather",
    "write_file",
    "read_file",
    "get_current_time",
    "scrape_webpage",
    "make_api_request",
    "query_database",
    "analyze_csv",
    "crawl_website",
    "search_web",
    "get_weather_no_api",
    "get_latest_news",
    "get_stock_price_no_api",
    "extract_product_details",
    "extract_faq_from_page",
]
