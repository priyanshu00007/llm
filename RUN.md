# How to Run ReAct Agent with Mistral AI

Quick start guide for running the ReAct Agent powered by **Mistral AI**.

---

## LLM: Mistral AI (Primary)

The agent uses **Mistral AI** cloud API by default for best performance.

*Alternative: Ollama for offline/local usage (optional)*

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- **Mistral AI API key** (get from https://console.mistral.ai/)

**For Offline/Local Usage (Optional):**
- Ollama installed (get from https://ollama.com/download)

---

## Step 1: Setup Environment

### 1.1 Navigate to project folder
```bash
cd react_agent
```

### 1.2 Create virtual environment
```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

### 1.3 Activate virtual environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 1.4 Install dependencies
```bash
pip install -r requirements.txt
```

---

## Step 2: Configure Mistral AI (Primary)

### 2.1 Copy environment template
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### 2.2 Edit `.env` file - Add Mistral API Key
```env
MISTRAL_API_KEY=your_actual_mistral_api_key_here
```

**Get your API key from:** https://console.mistral.ai/

### 2.3 (Optional) Use Different Mistral Model
```env
# Options: mistral-large-latest, mistral-medium-latest, mistral-small-latest
MISTRAL_MODEL=mistral-large-latest
```

### 2.4 Skip to Step 3

---

## Alternative: Local Ollama (Offline Mode)

### B.1 Install Ollama
Download and install from: https://ollama.com/download

### B.2 Pull a model
```bash
# Pull Mistral model (recommended)
ollama pull mistral

# Or pull other models:
ollama pull llama2
ollama pull codellama
ollama pull phi
```

### B.3 Verify Ollama is running
```bash
ollama list
```

You should see your downloaded models.

### B.4 Copy environment template
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### B.5 Edit `.env` file for Ollama
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

**Note:** No API key needed for Ollama!

---

## Step 2 (Optional): Add External API Keys

These are optional for additional tools:

```env
OPENWEATHER_API_KEY=your_key_here  # For weather tool
SERPAPI_API_KEY=your_key_here      # For search tool
```

---

## Step 3: Setup Project

Run the setup script to create sample data:
```bash
python setup.py
```

This creates:
- `data/` folder with sample database
- `outputs/` folder for file outputs

---

## Step 4: Run the Agent

### Option 1: Interactive CLI (Recommended)
```bash
python examples/interactive_cli.py
```

Then type queries like:
- `What is 1500 divided by 42?`
- `What's the weather in London?`
- `Write "Hello" to greeting.txt`
- `quit` to exit

### Option 2: Basic Examples
```bash
python examples/basic_usage.py
```

### Option 3: Advanced Examples
```bash
python examples/advanced_examples.py
```

### Option 4: Web Crawler Demo (No API Keys!)
```bash
python examples/web_crawler_demo.py
```

This demo shows:
- Web search without API keys
- Weather via web scraping
- News extraction
- Stock prices via scraping
- Deep website crawling

### Option 5: API Server
```bash
# Install uvicorn if not already installed
pip install uvicorn

# Run the API server
python -m uvicorn api:app --reload

# Open browser to: http://localhost:8000/docs
```

---

## Usage Examples

### Using Mistral AI (Default)
```python
from src.agent import create_agent

# Uses Mistral AI from .env configuration
agent = create_agent()

# Run queries
result = agent.run("Calculate 100 / 4")
print(result)
```

### Specify Mistral Model
```python
from src.agent import create_agent

# Use specific Mistral model
agent = create_agent(
    provider="mistral",
    model="mistral-large-latest"  # or mistral-medium-latest
)
result = agent.run("Calculate 100 / 4")
```

### Use Local Ollama (Offline)
```python
from src.agent import create_agent

# Switch to local Ollama
agent = create_agent(provider="ollama", model="mistral")
result = agent.run("Calculate 100 / 4")
```

### Multi-Step Tasks
```python
agent.run(
    "Get the weather in Tokyo, "
    "calculate the temperature in Fahrenheit, "
    "and save to weather_tokyo.txt"
)
```

---

## Common Commands

| Command | Description |
|---------|-------------|
| `python examples/interactive_cli.py` | Interactive chat mode |
| `python examples/basic_usage.py` | Run basic examples |
| `python examples/advanced_examples.py` | Run advanced examples |
| `python setup.py` | Create sample data |
| `python -m uvicorn api:app --reload` | Start API server |
| `pip install -r requirements.txt` | Install dependencies |

---

## Troubleshooting

### Error: "Mistral API key is required"
- Make sure `.env` file exists with `MISTRAL_API_KEY=your_key`
- Ensure virtual environment is activated
- OR switch to Ollama: Set `LLM_PROVIDER=ollama` in `.env`

### Ollama: "Connection refused" or "Cannot connect"
1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```
2. Check Ollama is installed:
   ```bash
   ollama --version
   ```
3. Verify model is downloaded:
   ```bash
   ollama list
   ollama pull mistral
   ```

### Ollama: "Model not found"
```bash
# Pull the model first
ollama pull mistral

# Or use a different model
ollama pull llama2
```

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "No module named 'tools'"
Run from project root directory:
```bash
cd react_agent
python examples/basic_usage.py
```

### Virtual environment not activating (Windows PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## File Structure After Setup

```
react_agent/
├── venv/                   # Virtual environment
├── data/
│   ├── sample_data.csv     # Sample CSV data
│   └── sample.db           # Sample SQLite database
├── outputs/                # Generated files go here
├── src/                    # Agent source code
├── tools/                  # Tool implementations
├── examples/               # Example scripts
├── .env                    # Your API keys (created by you)
└── requirements.txt        # Dependencies
```

---

## Next Steps

1. Try the interactive CLI: `python examples/interactive_cli.py`
2. Check available tools: type `tools` in the CLI
3. Run your own queries!

---

## Need Help?

Check the main README.md for detailed documentation.
