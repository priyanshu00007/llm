"""FastAPI backend for the ReAct Agent.

Start with:
    uvicorn api:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from src.agent import ReActAgent, create_agent

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("api")

# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------
_agent: ReActAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _agent
    logger.info("Initialising agent…")
    try:
        _agent = create_agent(verbose=False)
        logger.info("Agent ready. Provider: %s", _agent.provider)
    except Exception as exc:
        logger.warning("Agent init failed (will retry on first request): %s", exc)
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="ReAct Agent API",
    description="Autonomous AI Agent powered by Mistral AI or Ollama",
    version="2.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
_allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_agent() -> ReActAgent:
    global _agent
    if _agent is None:
        _agent = create_agent(verbose=False)
    return _agent


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RunRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000, description="Task for the agent")
    temperature: Optional[float] = Field(0.1, ge=0.0, le=2.0)
    max_iterations: Optional[int] = Field(10, ge=1, le=25)


class RunResponse(BaseModel):
    output: str
    status: str
    duration_ms: int
    provider: str


class ToolInfo(BaseModel):
    name: str
    description: str


class ToolsResponse(BaseModel):
    tools: list[ToolInfo]
    count: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["meta"])
async def root():
    return {
        "name": "ReAct Agent API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["meta"])
async def health():
    try:
        agent = _get_agent()
        return {"status": "healthy", "provider": agent.provider, "tools": len(agent.tools)}
    except Exception as exc:
        return {"status": "degraded", "error": str(exc)}


@app.get("/tools", response_model=ToolsResponse, tags=["tools"])
async def list_tools():
    try:
        agent = _get_agent()
        tools = agent.tool_descriptions()
        return {"tools": tools, "count": len(tools)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/run", response_model=RunResponse, tags=["agent"])
async def run_agent(req: RunRequest):
    """Run the agent synchronously and return the full result."""
    try:
        agent = _get_agent()
        result = await asyncio.get_event_loop().run_in_executor(
            None, agent.run, req.query
        )
        return RunResponse(
            output=result["output"],
            status=result["status"],
            duration_ms=result["duration_ms"],
            provider=agent.provider,
        )
    except Exception as exc:
        logger.exception("Unhandled error in /run")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/run/stream", tags=["agent"])
async def run_agent_stream(req: RunRequest):
    """
    Run the agent and stream the response as Server-Sent Events.

    Each event is a JSON object:
      {"type": "token"|"done"|"error", "data": "..."}
    """

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            agent = _get_agent()
            loop = asyncio.get_event_loop()

            # Run in thread pool so we don't block the event loop
            result = await loop.run_in_executor(None, agent.run, req.query)

            output: str = result["output"]

            # Stream word-by-word for a typewriter effect
            words = output.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                payload = json.dumps({"type": "token", "data": chunk})
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0.01)

            done_payload = json.dumps({
                "type": "done",
                "data": "",
                "status": result["status"],
                "duration_ms": result["duration_ms"],
            })
            yield f"data: {done_payload}\n\n"

        except Exception as exc:
            logger.exception("Stream error")
            err_payload = json.dumps({"type": "error", "data": str(exc)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
