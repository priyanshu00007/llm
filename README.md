# ReAct Agent with Mistral AI

A powerful autonomous agent built using the **ReAct (Reasoning + Acting)** pattern powered by **Mistral AI**.

*Also supports local Ollama for offline usage.*

## LLM: Mistral AI

**Primary: Mistral AI (Cloud)** - Best performance and accuracy

*Alternative: Ollama (Local) - Available for offline use*

---

## ReAct Pattern

**ReAct = Reasoning + Acting loop**

The LLM will:
1. Think (reason)
2. Decide which tool to use
3. Use the tool
4. Observe result
5. Repeat until goal is achieved

### Example Workflow

> "Get weather in London → calculate temperature in Fahrenheit → save to file"

```
Thought → I need London weather
Action → Use Weather Tool
Observation → London: 15°C

Thought → Convert to Fahrenheit
Action → Use Calculator (15 * 9/5 + 32)
Observation → 59°F

Thought → Save to file
Action → Use Write File Tool
Done ✅
```

---

# Core Components

1. **LLM**: Mistral AI (cloud) or Ollama (local)
2. **Tools**: 11 built-in tools (Calculator, Weather, File I/O, Web Scraping, API, Database, CSV, Email, DateTime)
3. **Agent**: ReAct pattern brain that decides which tool to use
4. **Memory** (optional): Conversation context
5. **Tracing**: LangSmith debug support

---

# Quick Start

## 1. Installation

```bash
# Clone/navigate to project
cd react_agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure Mistral AI

### Setup API Key
```bash
copy .env.example .env
# Edit .env and add your API key:
MISTRAL_API_KEY=your_mistral_api_key_here
```

Get your API key from: https://console.mistral.ai/

### (Optional) Use Local Ollama Instead
```bash
# Install Ollama from https://ollama.com/download
ollama pull mistral

# Edit .env:
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
```

## 3. Run

```bash
python setup.py                    # Setup sample data
python examples/interactive_cli.py # Interactive mode
```

---

# Features

- 🤖 **Mistral AI Powered** - Uses Mistral Large language model
- �️ **Advanced Web Crawler** - Search, crawl, extract data without API keys
- �️ **17 Built-in Tools** - Calculator, Weather, News, Stocks, Web Scraping, Database, API, CSV, Email
- 🧠 **ReAct Pattern** - Intelligent reasoning and acting loop
- 📝 **File Operations** - Read/write files for persistent storage
- 🌐 **Web Scraping** - Extract content from any webpage
- 📊 **Data Analysis** - CSV and SQL database analysis
- 🔧 **Extensible** - Easy to add custom tools
- 🦙 **Offline Mode** - Can use local Ollama when needed
- 🚀 **FastAPI Backend** - Optional web API

## 🆕 Web Crawler Tools (No API Keys!)

| Tool | What It Does | Example Query |
|------|--------------|---------------|
| `search_web` | Search Google/DuckDuckGo | `"Search for Python tutorials"` |
| `get_weather_no_api` | Weather via web scraping | `"Weather in London"` |
| `get_latest_news` | News without API keys | `"Latest tech news"` |
| `get_stock_price_no_api` | Stock prices via scraping | `"Stock price AAPL"` |
| `crawl_website` | Deep website crawling | `"Crawl https://example.com"` |
| `extract_product_details` | Product info from Amazon/eBay | `"Extract from product URL"` |
| `extract_faq_from_page` | FAQ extraction | `"Get FAQ from support page"` |

---

# Project Structure

```
react_agent/
├── src/
│   └── agent.py              # Main agent implementation
├── tools/
│   ├── calculator.py         # Math calculations
│   ├── email.py              # Email operations
│   ├── weather.py            # Weather API
│   ├── file_io.py            # File read/write
│   ├── datetime_tool.py      # Date/time utilities
│   ├── web_scraper.py        # Web scraping
│   ├── web_crawler.py        # Advanced web crawler (NEW!)
│   ├── api_request.py        # HTTP requests
│   ├── database.py           # SQLite queries
│   └── csv_analyzer.py       # CSV analysis
├── examples/
│   ├── basic_usage.py        # Basic examples
│   ├── advanced_examples.py  # Multi-step workflows
│   ├── interactive_cli.py    # Interactive CLI
│   └── web_crawler_demo.py   # Crawler demo (NEW!)
├── data/                     # Input data files
├── outputs/                  # Output files
├── api.py                    # FastAPI backend
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
├── RUN.md                    # Detailed run guide
└── README.md                 # This file
```

---

# Usage Examples

### Auto-detect from .env
```python
from src.agent import create_agent

agent = create_agent()
result = agent.run("Calculate 100 / 4")
```

### Force Cloud Mistral
```python
agent = create_agent(provider="mistral")
```

### Force Local Ollama
```python
agent = create_agent(provider="ollama", model="mistral")
```

### Multi-Step Task
```python
agent.run(
    "Get weather in London, convert to Fahrenheit, save to file"
)
```

---

# Available Tools

## Core Tools

| Tool | Description | Example |
|------|-------------|---------|
| `calculator` | Math calculations | `"1500 / 42"` |
| `get_weather` | Weather by city (API) | `"London"` |
| `get_current_time` | Current datetime | `None` |
| `write_file` | Save to file | `"Hello\|greeting.txt"` |
| `read_file` | Read from file | `"report.txt"` |
| `scrape_webpage` | Extract webpage | `"https://example.com"` |
| `make_api_request` | HTTP API call | `"https://api.com/data\|GET"` |
| `query_database` | SQL queries | `"SELECT * FROM users"` |
| `analyze_csv` | CSV analysis | `"describe\|data.csv"` |
| `send_email` | Email (mock) | `"Hello there"` |

## 🆕 Web Crawler Tools (No API Keys!)

| Tool | Description | Example |
|------|-------------|---------|
| `search_web` | Search web via scraping | `"Python tutorials"` |
| `get_weather_no_api` | Weather via scraping | `"Weather in Paris"` |
| `get_latest_news` | News via web search | `"Latest AI news"` |
| `get_stock_price_no_api` | Stock prices via scraping | `"AAPL stock price"` |
| `crawl_website` | Deep website crawl | `"https://docs.python.org"` |
| `extract_product_details` | E-commerce scraping | `"Amazon product URL"` |
| `extract_faq_from_page` | FAQ extraction | `"Support page URL"` |

---

# Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LLM_PROVIDER` | Yes | `mistral` or `ollama` |
| `MISTRAL_API_KEY` | If cloud | Mistral AI API key |
| `MISTRAL_MODEL` | No | `mistral:latest ` |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` |
| `OLLAMA_MODEL` | No | `mistral` |
| `OPENWEATHER_API_KEY` | No | Weather tool API |

---

# Documentation

- **RUN.md** - Complete setup and running guide
- **Examples/** - Working code examples
- **.env.example** - Configuration template

---

# License

MIT License - Free to use and modify.
