import { useState, useEffect, useRef, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Wrench, RotateCcw, Download, ChevronRight } from "lucide-react";
import { MessageBubble } from "./components/MessageBubble";
import { ChatInput } from "./components/ChatInput";
import { StatusBadge } from "./components/StatusBadge";
import { ToolsPanel } from "./components/ToolsPanel";
import { Sidebar, type ChatSession } from "./components/Sidebar";
import { fetchHealth, fetchTools, runQuery } from "./api";
import type { Message, HealthStatus, ToolInfo } from "./types";

// ── helpers ──────────────────────────────────────────────────────────────────

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

function newSession(firstMessage?: string): ChatSession {
  return {
    id: uid(),
    title: firstMessage ? firstMessage.slice(0, 40) : "New Chat",
    createdAt: new Date(),
    messageCount: 0,
  };
}

const WELCOME: Message = {
  id: "welcome",
  role: "assistant",
  content:
    "Hi! I'm your ReAct Agent powered by **Mistral AI**.\n\n" +
    "I can reason through multi-step tasks using tools like web search, weather, " +
    "calculator, file I/O, databases, CSV analysis, and more.\n\n" +
    "What would you like me to help with?",
  status: "done",
  timestamp: new Date(),
};

// ── component ─────────────────────────────────────────────────────────────────

export default function App() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const [messageMap, setMessageMap] = useState<Record<string, Message[]>>({});

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<HealthStatus>({ status: "offline" });
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [toolsOpen, setToolsOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const messages = messageMap[activeId] ?? [WELCOME];

  // ── init ──────────────────────────────────────────────────────────────────

  useEffect(() => {
    const session = newSession();
    setSessions([session]);
    setActiveId(session.id);
    setMessageMap({ [session.id]: [WELCOME] });

    fetchHealth().then(setHealth);
    fetchTools().then(setTools).catch(() => {});

    const interval = setInterval(() => fetchHealth().then(setHealth), 30_000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── session management ────────────────────────────────────────────────────

  const handleNewSession = useCallback(() => {
    const s = newSession();
    setSessions((prev) => [s, ...prev]);
    setActiveId(s.id);
    setMessageMap((prev) => ({ ...prev, [s.id]: [WELCOME] }));
    setInput("");
  }, []);

  const handleSelectSession = useCallback((id: string) => {
    setActiveId(id);
    setInput("");
  }, []);

  const handleDeleteSession = useCallback(
    (id: string) => {
      setSessions((prev) => prev.filter((s) => s.id !== id));
      setMessageMap((prev) => {
        const next = { ...prev };
        delete next[id];
        return next;
      });
      if (id === activeId) {
        handleNewSession();
      }
    },
    [activeId, handleNewSession]
  );

  // ── send message ──────────────────────────────────────────────────────────

  const handleSubmit = useCallback(async () => {
    const query = input.trim();
    if (!query || loading) return;

    setInput("");
    setLoading(true);

    const userMsg: Message = {
      id: uid(),
      role: "user",
      content: query,
      status: "done",
      timestamp: new Date(),
    };

    const assistantId = uid();
    const assistantMsg: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      status: "streaming",
      timestamp: new Date(),
    };

    // Update messages
    setMessageMap((prev) => {
      const existing = prev[activeId] ?? [WELCOME];
      return { ...prev, [activeId]: [...existing, userMsg, assistantMsg] };
    });

    // Update session title on first real message
    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeId
          ? {
              ...s,
              title: s.messageCount === 0 ? query.slice(0, 40) : s.title,
              messageCount: s.messageCount + 1,
            }
          : s
      )
    );

    try {
      await runQuery(
        query,
        // onToken
        (token) => {
          setMessageMap((prev) => {
            const msgs = [...(prev[activeId] ?? [])];
            const idx = msgs.findIndex((m) => m.id === assistantId);
            if (idx !== -1) {
              msgs[idx] = { ...msgs[idx], content: msgs[idx].content + token };
            }
            return { ...prev, [activeId]: msgs };
          });
        },
        // onDone
        (duration_ms) => {
          setMessageMap((prev) => {
            const msgs = [...(prev[activeId] ?? [])];
            const idx = msgs.findIndex((m) => m.id === assistantId);
            if (idx !== -1) {
              msgs[idx] = { ...msgs[idx], status: "done", duration_ms };
            }
            return { ...prev, [activeId]: msgs };
          });
          setLoading(false);
        },
        // onError
        (err) => {
          setMessageMap((prev) => {
            const msgs = [...(prev[activeId] ?? [])];
            const idx = msgs.findIndex((m) => m.id === assistantId);
            if (idx !== -1) {
              msgs[idx] = {
                ...msgs[idx],
                content: `Error: ${err}`,
                status: "error",
              };
            }
            return { ...prev, [activeId]: msgs };
          });
          setLoading(false);
        }
      );
    } catch (err) {
      setMessageMap((prev) => {
        const msgs = [...(prev[activeId] ?? [])];
        const idx = msgs.findIndex((m) => m.id === assistantId);
        if (idx !== -1) {
          msgs[idx] = {
            ...msgs[idx],
            content: `Unexpected error: ${err}`,
            status: "error",
          };
        }
        return { ...prev, [activeId]: msgs };
      });
      setLoading(false);
    }
  }, [input, loading, activeId]);

  const handleStop = useCallback(() => {
    abortRef.current?.abort();
    setLoading(false);
    setMessageMap((prev) => {
      const msgs = [...(prev[activeId] ?? [])];
      const last = msgs[msgs.length - 1];
      if (last?.status === "streaming") {
        msgs[msgs.length - 1] = { ...last, status: "done", content: last.content + " *(stopped)*" };
      }
      return { ...prev, [activeId]: msgs };
    });
  }, [activeId]);

  const handleClearChat = useCallback(() => {
    setMessageMap((prev) => ({ ...prev, [activeId]: [WELCOME] }));
    setSessions((prev) =>
      prev.map((s) => (s.id === activeId ? { ...s, messageCount: 0 } : s))
    );
  }, [activeId]);

  const handleExport = useCallback(() => {
    const text = messages
      .filter((m) => m.id !== "welcome")
      .map((m) => `[${m.role.toUpperCase()}]\n${m.content}`)
      .join("\n\n---\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `chat-${activeId}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }, [messages, activeId]);

  // ── render ────────────────────────────────────────────────────────────────

  return (
    <div className="flex h-screen bg-slate-900 overflow-hidden">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 256, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <Sidebar
              sessions={sessions}
              activeId={activeId}
              onSelect={handleSelectSession}
              onNew={handleNewSession}
              onDelete={handleDeleteSession}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen((v) => !v)}
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              aria-label="Toggle sidebar"
            >
              <ChevronRight
                size={16}
                className={`transition-transform ${sidebarOpen ? "rotate-180" : ""}`}
              />
            </button>
            <StatusBadge health={health} />
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={handleExport}
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              title="Export chat"
              aria-label="Export chat"
            >
              <Download size={15} />
            </button>
            <button
              onClick={handleClearChat}
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              title="Clear chat"
              aria-label="Clear chat"
            >
              <RotateCcw size={15} />
            </button>
            <button
              onClick={() => setToolsOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700
                         text-slate-300 text-xs font-medium transition-colors border border-slate-700"
              aria-label="View tools"
            >
              <Wrench size={13} />
              Tools
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-5">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="px-4 pb-5 pt-3 border-t border-slate-800 bg-slate-900/80 backdrop-blur-sm">
          <div className="max-w-3xl mx-auto">
            <ChatInput
              value={input}
              onChange={setInput}
              onSubmit={handleSubmit}
              onStop={handleStop}
              loading={loading}
              disabled={health.status === "offline"}
            />
          </div>
        </div>
      </div>

      {/* Tools panel */}
      <ToolsPanel tools={tools} open={toolsOpen} onClose={() => setToolsOpen(false)} />
    </div>
  );
}
