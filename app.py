"""
ReAct Agent — Streamlit UI
Run: streamlit run app.py
"""

from __future__ import annotations

import os
import re
import sys
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# ── path & env ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# ── page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="ReAct Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 0.5rem; max-width: 1200px; }

/* sidebar */
[data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #1e293b; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }

/* chat bubbles */
.user-msg {
    background: linear-gradient(135deg,#0284c7,#0ea5e9);
    color: #fff;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 6px 0 2px 18%;
    font-size: .9rem;
    line-height: 1.65;
    box-shadow: 0 2px 10px rgba(14,165,233,.2);
    word-wrap: break-word;
}
.agent-msg {
    background: #1e293b;
    border: 1px solid #334155;
    color: #e2e8f0;
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 6px 18% 2px 0;
    font-size: .9rem;
    line-height: 1.75;
    box-shadow: 0 2px 10px rgba(0,0,0,.15);
    word-wrap: break-word;
}
.agent-msg code {
    background: #0f172a; border: 1px solid #334155; border-radius: 4px;
    padding: 1px 6px; font-family: 'JetBrains Mono',monospace;
    font-size: .82rem; color: #7dd3fc;
}
.agent-msg pre {
    background: #0f172a; border: 1px solid #334155; border-radius: 8px;
    padding: 12px; overflow-x: auto; font-family: 'JetBrains Mono',monospace;
    font-size: .82rem; color: #e2e8f0; margin: 8px 0;
}
.err-msg {
    background: #1a0505; border: 1px solid #7f1d1d; color: #fca5a5;
    padding: 12px 16px; border-radius: 12px; margin: 6px 18% 2px 0;
    font-size: .88rem;
}
.msg-meta { font-size: .7rem; color: #475569; margin: 0 4px 10px 4px; }

/* thinking */
.thinking {
    display:flex; align-items:center; gap:10px;
    background:#1e293b; border:1px solid #334155;
    border-radius:12px; padding:12px 16px;
    margin:6px 18% 2px 0; width:fit-content;
    font-size:.85rem; color:#64748b;
}
.dot { width:8px; height:8px; border-radius:50%; background:#0ea5e9;
       display:inline-block; margin:0 2px;
       animation: blink 1.2s infinite; }
.dot:nth-child(2){animation-delay:.2s}
.dot:nth-child(3){animation-delay:.4s}
@keyframes blink{0%,80%,100%{opacity:.3;transform:translateY(0)}
                 40%{opacity:1;transform:translateY(-5px)}}

/* stat card */
.stat { background:#1e293b; border:1px solid #334155; border-radius:10px;
        padding:12px; text-align:center; }
.stat-v { font-size:1.5rem; font-weight:700; color:#38bdf8; }
.stat-l { font-size:.72rem; color:#64748b; margin-top:2px; }

/* welcome */
.welcome {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    border:1px solid #334155; border-radius:16px;
    padding:36px; text-align:center; margin:24px 0;
}
.welcome h2 { color:#f1f5f9; font-size:1.6rem; margin-bottom:8px; }
.welcome p  { color:#94a3b8; font-size:.92rem; line-height:1.7; }

/* input */
.stTextArea textarea {
    background:#1e293b !important; border:1px solid #334155 !important;
    border-radius:12px !important; color:#e2e8f0 !important;
    font-family:'Inter',sans-serif !important; font-size:.9rem !important;
}
.stTextArea textarea:focus {
    border-color:#0ea5e9 !important;
    box-shadow:0 0 0 2px rgba(14,165,233,.15) !important;
}
.stButton>button { border-radius:10px !important; font-weight:600 !important; }
hr { border-color:#1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ── agent loader (cached across reruns) ──────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_agent(provider: str = "auto", temperature: float = 0.1, max_iterations: int = 10):
    from src.agent import create_agent
    p = None if provider == "auto" else provider
    return create_agent(provider=p, temperature=temperature,
                        verbose=False, max_iterations=max_iterations)


# ── session state defaults ────────────────────────────────────────────────────
_DEFAULTS: dict = {
    "messages": [],          # [{role, content, ts, duration_ms?}]
    "history": [],           # [{id, title, messages, created}]
    "session_id": None,
    "total_queries": 0,
    "total_ms": 0,
    "form_key": 0,
    "_prefill": "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── helpers ───────────────────────────────────────────────────────────────────
TOOL_ICONS = {
    "calculator": "🧮", "send_email": "📧",
    "get_weather": "🌤️", "get_weather_no_api": "🌦️",
    "write_file": "📝", "read_file": "📂",
    "get_current_time": "🕐", "scrape_webpage": "🌐",
    "make_api_request": "🔌", "query_database": "🗄️",
    "analyze_csv": "📊", "search_web": "🔍",
    "crawl_website": "🕷️", "get_latest_news": "📰",
    "get_stock_price_no_api": "📈", "extract_product_details": "🛒",
    "extract_faq_from_page": "❓",
}

SUGGESTIONS = [
    ("🌤️", "What's the weather in Tokyo right now?"),
    ("🔍", "Search the web for latest AI news in 2025"),
    ("🧮", "Calculate compound interest: $10,000 at 7% for 10 years"),
    ("📰", "Get the latest technology news headlines"),
    ("📈", "What is the current stock price of AAPL?"),
    ("🕐", "What is today's date and current time?"),
    ("🌐", "Scrape https://httpbin.org/json and summarize it"),
    ("🗄️", "List all tables in the database"),
    ("📊", "Analyze the sample CSV file — show describe stats"),
    ("🕷️", "Crawl https://example.com and extract all links"),
]


def _ts() -> str:
    return datetime.now().strftime("%H:%M")


def _fmt_ms(ms: int) -> str:
    return f"{ms / 1000:.1f}s" if ms >= 1000 else f"{ms}ms"


def _uid() -> str:
    import random, string
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def _save_session():
    msgs = st.session_state.messages
    if not msgs:
        return
    sid = st.session_state.session_id or _uid()
    st.session_state.session_id = sid
    title = msgs[0]["content"][:38] + ("…" if len(msgs[0]["content"]) > 38 else "")
    for s in st.session_state.history:
        if s["id"] == sid:
            s["messages"] = list(msgs)
            s["title"] = title
            return
    st.session_state.history.insert(0, {
        "id": sid, "title": title,
        "messages": list(msgs),
        "created": datetime.now().strftime("%b %d %H:%M"),
    })


def _new_chat():
    _save_session()
    st.session_state.messages = []
    st.session_state.session_id = _uid()


def _load_session(sid: str):
    for s in st.session_state.history:
        if s["id"] == sid:
            st.session_state.messages = list(s["messages"])
            st.session_state.session_id = sid
            return


def _render_agent_text(text: str) -> str:
    """Convert plain agent output to safe HTML with code block support."""
    import html as _html
    # escape HTML entities first
    out = _html.escape(text)
    # fenced code blocks  ```lang\n...\n```
    out = re.sub(
        r"```(?:\w+)?\n?(.*?)```",
        lambda m: f"<pre><code>{m.group(1)}</code></pre>",
        out, flags=re.DOTALL,
    )
    # inline `code`
    out = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", out)
    # **bold**
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    # newlines → <br>
    out = out.replace("\n", "<br>")
    return out


# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # brand header
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;
                padding:6px 0 18px;border-bottom:1px solid #1e293b;margin-bottom:14px">
      <div style="width:42px;height:42px;border-radius:12px;flex-shrink:0;
                  background:linear-gradient(135deg,#0ea5e9,#8b5cf6);
                  display:flex;align-items:center;justify-content:center;font-size:22px">⚡</div>
      <div>
        <div style="font-weight:700;font-size:1rem;color:#f1f5f9;line-height:1.2">ReAct Agent</div>
        <div style="font-size:.72rem;color:#475569">Mistral AI · Ollama</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # new chat
    if st.button("＋  New Chat", use_container_width=True, type="primary"):
        _new_chat()
        st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── settings ──
    with st.expander("⚙️  Settings", expanded=False):
        env_provider = os.getenv("LLM_PROVIDER", "mistral")
        provider_choice = st.selectbox(
            "LLM Provider",
            ["auto", "mistral", "ollama"],
            index=["auto", "mistral", "ollama"].index(
                "auto" if env_provider not in ("mistral", "ollama") else env_provider
            ),
            help="'auto' reads LLM_PROVIDER from .env",
        )
        temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05,
                                help="Higher = more creative, lower = more focused")
        max_iter = st.slider("Max Iterations", 3, 25, 10,
                             help="Max reasoning steps the agent can take")
        st.caption("Settings apply to the next message sent.")

    st.markdown("---")

    # ── chat history ──
    st.markdown(
        "<div style='font-size:.72rem;color:#475569;font-weight:600;"
        "letter-spacing:.06em;margin-bottom:8px'>CHAT HISTORY</div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.history:
        st.markdown(
            "<div style='font-size:.8rem;color:#334155;text-align:center;padding:14px 0'>"
            "No chats yet</div>",
            unsafe_allow_html=True,
        )
    else:
        for sess in st.session_state.history[:25]:
            is_active = sess["id"] == st.session_state.session_id
            c1, c2 = st.columns([5, 1])
            with c1:
                label = ("▶ " if is_active else "") + sess["title"]
                if st.button(label, key=f"h_{sess['id']}", use_container_width=True):
                    _save_session()
                    _load_session(sess["id"])
                    st.rerun()
            with c2:
                if st.button("✕", key=f"d_{sess['id']}", help="Delete"):
                    st.session_state.history = [
                        x for x in st.session_state.history if x["id"] != sess["id"]
                    ]
                    if sess["id"] == st.session_state.session_id:
                        _new_chat()
                    st.rerun()

    st.markdown("---")

    # ── tools panel ──
    with st.expander("🔧  Available Tools", expanded=False):
        try:
            _ag = load_agent(provider_choice, temperature, max_iter)
            for t in _ag.tools:
                icon = TOOL_ICONS.get(t.name, "🔧")
                desc_short = t.description.split(".")[0]
                st.markdown(
                    f"<div style='padding:5px 0;border-bottom:1px solid #1e293b'>"
                    f"<span style='font-size:.85rem'>{icon} "
                    f"<code style='color:#7dd3fc;background:#0f172a;"
                    f"padding:1px 5px;border-radius:4px'>{t.name}</code></span>"
                    f"<div style='font-size:.7rem;color:#475569;margin-top:2px'>{desc_short}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.error(f"Agent not ready: {e}")

    st.markdown("---")

    # ── session stats ──
    st.markdown(
        "<div style='font-size:.72rem;color:#475569;font-weight:600;"
        "letter-spacing:.06em;margin-bottom:8px'>SESSION STATS</div>",
        unsafe_allow_html=True,
    )
    q = st.session_state.total_queries
    avg_ms = st.session_state.total_ms // max(q, 1)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='stat'><div class='stat-v'>{q}</div>"
            f"<div class='stat-l'>Queries</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='stat'><div class='stat-v'>{_fmt_ms(avg_ms)}</div>"
            f"<div class='stat-l'>Avg Time</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<br><div style='font-size:.68rem;color:#1e293b;text-align:center'>"
        "ReAct Agent v2.0</div>",
        unsafe_allow_html=True,
    )


# ── main header ───────────────────────────────────────────────────────────────
h1, h2, h3 = st.columns([5, 3, 2])

with h1:
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;padding:4px 0'>"
        "<span style='font-size:1.35rem;font-weight:700;color:#f1f5f9'>⚡ ReAct Agent</span>"
        "<span style='font-size:.75rem;color:#475569;margin-top:2px'>Reasoning + Acting</span>"
        "</div>",
        unsafe_allow_html=True,
    )

with h2:
    # live status badge
    try:
        _ag = load_agent(provider_choice, temperature, max_iter)
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:6px;padding:7px 14px;"
            f"background:#0a1f0f;border:1px solid #166534;border-radius:20px;"
            f"font-size:.75rem;color:#4ade80;margin-top:6px;width:fit-content'>"
            f"<span style='width:7px;height:7px;border-radius:50%;background:#4ade80;"
            f"animation:pulse 2s infinite'></span>"
            f"{_ag.provider} · {len(_ag.tools)} tools ready"
            f"</div>"
            f"<style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}</style>",
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(
            "<div style='display:flex;align-items:center;gap:6px;padding:7px 14px;"
            "background:#1a0505;border:1px solid #7f1d1d;border-radius:20px;"
            "font-size:.75rem;color:#f87171;margin-top:6px;width:fit-content'>"
            "<span style='width:7px;height:7px;border-radius:50%;background:#f87171'></span>"
            "Agent offline — check .env"
            "</div>",
            unsafe_allow_html=True,
        )

with h3:
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear current chat"):
            st.session_state.messages = []
            st.rerun()
    with col_b:
        if st.button("💾 Save", use_container_width=True, help="Save chat to history"):
            _save_session()
            st.success("Saved!", icon="✅")

st.markdown("<hr style='margin:8px 0 14px'>", unsafe_allow_html=True)


# ── chat messages ─────────────────────────────────────────────────────────────
msgs = st.session_state.messages

if not msgs:
    # welcome screen
    st.markdown("""
    <div class="welcome">
      <div style="font-size:3.5rem;margin-bottom:14px">⚡</div>
      <h2>ReAct Agent</h2>
      <p>
        An autonomous AI that <strong style="color:#38bdf8">reasons</strong> through problems
        and <strong style="color:#a78bfa">acts</strong> using 17 built-in tools.<br>
        Web search · Weather · Calculator · Database · CSV · File I/O · Stock prices · News · and more.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;color:#475569;font-size:.82rem;margin:4px 0 12px'>Try one of these:</div>",
        unsafe_allow_html=True,
    )

    # suggestion grid — 2 columns
    rows = [SUGGESTIONS[i:i+2] for i in range(0, len(SUGGESTIONS), 2)]
    for row in rows:
        cols = st.columns(len(row))
        for col, (icon, text) in zip(cols, row):
            with col:
                if st.button(f"{icon}  {text}", use_container_width=True, key=f"sug_{text[:20]}"):
                    st.session_state["_prefill"] = text
                    st.rerun()

else:
    # render conversation
    for msg in msgs:
        role = msg["role"]
        content = msg["content"]
        ts = msg.get("ts", "")
        dur = msg.get("duration_ms")

        if role == "user":
            import html as _html
            safe = _html.escape(content).replace("\n", "<br>")
            st.markdown(
                f'<div class="user-msg">{safe}</div>'
                f'<div class="msg-meta" style="text-align:right">You · {ts}</div>',
                unsafe_allow_html=True,
            )

        elif role == "assistant":
            rendered = _render_agent_text(content)
            dur_str = f" · ⏱ {_fmt_ms(dur)}" if dur else ""
            st.markdown(
                f'<div class="agent-msg">{rendered}</div>'
                f'<div class="msg-meta">🤖 Agent{dur_str} · {ts}</div>',
                unsafe_allow_html=True,
            )

        elif role == "error":
            import html as _html
            safe = _html.escape(content).replace("\n", "<br>")
            st.markdown(
                f'<div class="err-msg">⚠️ {safe}</div>',
                unsafe_allow_html=True,
            )


# ── input form ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

prefill = st.session_state.pop("_prefill", "")

with st.form(key=f"chat_{st.session_state.form_key}", clear_on_submit=True):
    inp_col, btn_col = st.columns([9, 1])
    with inp_col:
        user_input = st.text_area(
            label="Message",
            value=prefill,
            placeholder="Ask the agent anything… (Shift+Enter for new line, then click Send)",
            height=90,
            label_visibility="collapsed",
        )
    with btn_col:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Send ➤", use_container_width=True, type="primary")

st.markdown(
    "<div style='text-align:center;font-size:.7rem;color:#334155;margin-top:4px'>"
    "Agent may take 15–60 s for complex multi-step tasks"
    "</div>",
    unsafe_allow_html=True,
)


# ── handle send ───────────────────────────────────────────────────────────────
if submitted and user_input and user_input.strip():
    query = user_input.strip()

    if not st.session_state.session_id:
        st.session_state.session_id = _uid()

    # append user message
    st.session_state.messages.append({"role": "user", "content": query, "ts": _ts()})

    # thinking placeholder
    thinking_ph = st.empty()
    thinking_ph.markdown(
        '<div class="thinking">'
        '<span class="dot"></span><span class="dot"></span><span class="dot"></span>'
        '&nbsp; Agent is thinking…'
        '</div>',
        unsafe_allow_html=True,
    )

    try:
        agent = load_agent(provider_choice, temperature, max_iter)
        t0 = time.monotonic()
        result = agent.run(query)
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        thinking_ph.empty()

        output = result.get("output", str(result))
        status = result.get("status", "success")
        duration_ms = result.get("duration_ms", elapsed_ms)

        if status == "error":
            st.session_state.messages.append({
                "role": "error", "content": output, "ts": _ts(),
            })
        else:
            st.session_state.messages.append({
                "role": "assistant", "content": output,
                "ts": _ts(), "duration_ms": duration_ms,
            })
            st.session_state.total_queries += 1
            st.session_state.total_ms += duration_ms

    except Exception as exc:
        thinking_ph.empty()
        st.session_state.messages.append({
            "role": "error",
            "content": f"Unexpected error: {exc}\n\nCheck your .env file and make sure the LLM provider is configured.",
            "ts": _ts(),
        })

    _save_session()
    st.session_state.form_key += 1
    st.rerun()
