import { motion } from "framer-motion";
import { Plus, Trash2, MessageSquare, Zap } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

export interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
  messageCount: number;
}

interface Props {
  sessions: ChatSession[];
  activeId: string;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export function Sidebar({ sessions, activeId, onSelect, onNew, onDelete }: Props) {
  return (
    <aside className="w-64 shrink-0 bg-slate-950 border-r border-slate-800 flex flex-col h-full">
      {/* Brand */}
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-500/30 to-violet-500/30 border border-sky-500/30 flex items-center justify-center">
            <Zap size={16} className="text-sky-400" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-100 tracking-tight">ReAct Agent</p>
            <p className="text-xs text-slate-500">Mistral AI · Ollama</p>
          </div>
        </div>
      </div>

      {/* New chat button */}
      <div className="p-3">
        <button
          onClick={onNew}
          className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl
                     bg-sky-600 hover:bg-sky-500 active:bg-sky-700
                     text-white text-sm font-semibold transition-all duration-150 shadow-lg shadow-sky-900/30"
        >
          <Plus size={15} />
          New Chat
        </button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto px-2 pb-4 space-y-0.5">
        {sessions.length === 0 && (
          <div className="flex flex-col items-center gap-2 py-10 text-slate-600">
            <MessageSquare size={24} strokeWidth={1.5} />
            <p className="text-xs">No chats yet</p>
          </div>
        )}

        {sessions.map((s) => (
          <motion.div
            key={s.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.18 }}
            onClick={() => onSelect(s.id)}
            className={`group relative flex items-start gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-150
              ${s.id === activeId
                ? "bg-slate-800 border border-slate-700 shadow-sm"
                : "hover:bg-slate-800/50 border border-transparent"
              }`}
          >
            <MessageSquare
              size={13}
              className={`mt-0.5 shrink-0 ${s.id === activeId ? "text-sky-400" : "text-slate-600"}`}
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-slate-300 truncate leading-snug">{s.title}</p>
              <p className="text-xs text-slate-600 mt-0.5">
                {s.messageCount} msg · {formatDistanceToNow(s.createdAt, { addSuffix: true })}
              </p>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(s.id); }}
              className="opacity-0 group-hover:opacity-100 absolute right-2 top-2.5 p-1 rounded-lg
                         hover:bg-red-500/20 text-slate-500 hover:text-red-400 transition-all"
              aria-label="Delete chat"
            >
              <Trash2 size={11} />
            </button>
          </motion.div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-800">
        <p className="text-xs text-slate-600 text-center">ReAct Agent v2.0</p>
      </div>
    </aside>
  );
}
