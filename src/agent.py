"""ReAct Agent — supports Mistral AI (cloud) and Ollama (local)."""

from __future__ import annotations

import logging
import os
import sys
import time
from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import (
    analyze_csv,
    calculator,
    crawl_website,
    extract_faq_from_page,
    extract_product_details,
    get_current_time,
    get_latest_news,
    get_stock_price_no_api,
    get_weather,
    get_weather_no_api,
    make_api_request,
    query_database,
    read_file,
    scrape_webpage,
    search_web,
    send_email,
    write_file,
)

load_dotenv()
logger = logging.getLogger(__name__)

_REACT_TEMPLATE = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

REACT_PROMPT = PromptTemplate.from_template(_REACT_TEMPLATE)


def _build_tools() -> list[Tool]:
    """Build and return all LangChain Tool objects."""
    return [
        Tool(
            name="calculator",
            func=calculator,
            description=(
                "Evaluate mathematical expressions. "
                'Input: expression string like "500/65000", "sqrt(16)", "2**3". '
                "Returns the numeric result."
            ),
        ),
        Tool(
            name="send_email",
            func=lambda x: send_email("user@example.com", "Agent Notification", x),
            description=(
                "Send an email notification. "
                "Input: message body as a plain string. "
                "The email is saved to the outputs/ folder."
            ),
        ),
        Tool(
            name="get_weather",
            func=get_weather,
            description=(
                "Get current weather via OpenWeather API (requires OPENWEATHER_API_KEY). "
                'Input: city name like "London" or "New York". '
                "Returns temperature, conditions, humidity, wind speed."
            ),
        ),
        Tool(
            name="write_file",
            func=write_file,
            description=(
                "Write text to a file in outputs/. "
                "Input: 'content|filename.txt' or just 'content' (auto-named). "
                "Returns the saved file path."
            ),
        ),
        Tool(
            name="read_file",
            func=read_file,
            description=(
                "Read a file from outputs/ or data/. "
                'Input: filename like "report.txt" or "data.csv". '
                "Returns file contents."
            ),
        ),
        Tool(
            name="get_current_time",
            func=get_current_time,
            description=(
                "Get the current date and time. "
                "Input: any string (ignored). "
                "Returns: YYYY-MM-DD HH:MM:SS."
            ),
        ),
        Tool(
            name="scrape_webpage",
            func=scrape_webpage,
            description=(
                "Extract text content from a URL. "
                'Input: full URL like "https://example.com". '
                "Returns page title and main text."
            ),
        ),
        Tool(
            name="make_api_request",
            func=make_api_request,
            description=(
                "Make an HTTP request. "
                "Input: 'URL' or 'URL|METHOD' or 'URL|METHOD|{json_body}'. "
                "Default method is GET. Returns status code and response body."
            ),
        ),
        Tool(
            name="query_database",
            func=lambda x: query_database(
                x.split("|")[0], x.split("|")[1] if "|" in x else "database.db"
            ),
            description=(
                "Execute a SQL query on a SQLite database. "
                "Input: 'SELECT * FROM table' or 'SQL|db_file.db'. "
                "Returns formatted results table."
            ),
        ),
        Tool(
            name="analyze_csv",
            func=lambda x: analyze_csv(
                x.split("|")[0] if "|" in x else x,
                x.split("|")[1] if "|" in x else "",
            ),
            description=(
                "Analyze a CSV file with pandas. "
                "Input: 'operation|filename.csv'. "
                "Operations: describe, head, tail, columns, info, shape, nulls, "
                "value_counts:col, mean, mean:col, sum, sum:col."
            ),
        ),
        Tool(
            name="search_web",
            func=search_web,
            description=(
                "Search the web (no API key needed). "
                'Input: search query like "latest AI news". '
                "Returns titles, URLs, and snippets."
            ),
        ),
        Tool(
            name="crawl_website",
            func=crawl_website,
            description=(
                "Deep-crawl a webpage: extract content, links, and tables. "
                'Input: full URL like "https://docs.python.org". '
                "Returns content preview, link list, and table count."
            ),
        ),
        Tool(
            name="get_weather_no_api",
            func=get_weather_no_api,
            description=(
                "Get weather via web scraping — no API key required. "
                'Input: city name like "Tokyo". '
                "Returns temperature, condition, humidity, wind."
            ),
        ),
        Tool(
            name="get_latest_news",
            func=get_latest_news,
            description=(
                "Fetch latest news headlines — no API key required. "
                'Input: topic like "technology" or empty for general news. '
                "Returns headlines with summaries and sources."
            ),
        ),
        Tool(
            name="get_stock_price_no_api",
            func=get_stock_price_no_api,
            description=(
                "Get a stock price via web scraping — no API key required. "
                'Input: ticker symbol like "AAPL" or "TSLA". '
                "Returns current price and change percentage."
            ),
        ),
        Tool(
            name="extract_product_details",
            func=extract_product_details,
            description=(
                "Extract product info from an e-commerce page. "
                "Input: product page URL. "
                "Returns title, price, rating, and description."
            ),
        ),
        Tool(
            name="extract_faq_from_page",
            func=extract_faq_from_page,
            description=(
                "Extract FAQ Q&A pairs from a webpage. "
                "Input: URL containing FAQ content. "
                "Returns list of question/answer pairs."
            ),
        ),
    ]


def _create_llm(provider: str | None = None, **kwargs: Any):
    """Instantiate the LLM based on provider."""
    provider = (provider or os.getenv("LLM_PROVIDER", "mistral")).lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        model = kwargs.get("model") or os.getenv("OLLAMA_MODEL", "mistral")
        base_url = kwargs.get("base_url") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        temperature = kwargs.get("temperature", 0.1)
        logger.info("Using Ollama: %s @ %s", model, base_url)
        return ChatOllama(model=model, base_url=base_url, temperature=temperature)

    from langchain_mistralai import ChatMistralAI

    model = kwargs.get("model") or os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    api_key = kwargs.get("api_key") or os.getenv("MISTRAL_API_KEY")
    temperature = kwargs.get("temperature", 0.1)

    if not api_key:
        raise ValueError(
            "MISTRAL_API_KEY is required. Set it in .env or use LLM_PROVIDER=ollama."
        )
    logger.info("Using Mistral cloud: %s", model)
    return ChatMistralAI(model=model, temperature=temperature, api_key=api_key)


class ReActAgent:
    """Autonomous ReAct agent backed by Mistral AI or Ollama."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.1,
        api_key: str | None = None,
        base_url: str | None = None,
        verbose: bool = False,
        max_iterations: int = 10,
    ) -> None:
        self.provider = (provider or os.getenv("LLM_PROVIDER", "mistral")).lower()

        llm_kwargs = {
            k: v
            for k, v in dict(
                model=model,
                temperature=temperature,
                api_key=api_key,
                base_url=base_url,
            ).items()
            if v is not None
        }

        self.llm = _create_llm(self.provider, **llm_kwargs)
        self.tools = _build_tools()

        agent = create_react_agent(self.llm, self.tools, REACT_PROMPT)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=verbose,
            handle_parsing_errors=True,
            max_iterations=max_iterations,
            early_stopping_method="generate",
        )

    def run(self, query: str) -> dict[str, Any]:
        """
        Execute a query and return a structured result.

        Returns:
            {"output": str, "status": "success"|"error", "duration_ms": int}
        """
        start = time.monotonic()
        try:
            result = self.executor.invoke({"input": query})
            return {
                "output": result.get("output", str(result)),
                "status": "success",
                "duration_ms": int((time.monotonic() - start) * 1000),
            }
        except Exception as exc:
            logger.exception("Agent error for query: %s", query)
            return {
                "output": f"Agent error: {exc}",
                "status": "error",
                "duration_ms": int((time.monotonic() - start) * 1000),
            }

    def list_tools(self) -> list[str]:
        return [t.name for t in self.tools]

    def tool_descriptions(self) -> list[dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self.tools]


def create_agent(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.1,
    api_key: str | None = None,
    base_url: str | None = None,
    verbose: bool = False,
    max_iterations: int = 10,
) -> ReActAgent:
    """Factory function — create and return a ReActAgent."""
    return ReActAgent(
        provider=provider,
        model=model,
        temperature=temperature,
        api_key=api_key,
        base_url=base_url,
        verbose=verbose,
        max_iterations=max_iterations,
    )
