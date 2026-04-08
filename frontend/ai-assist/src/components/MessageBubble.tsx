import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, User, AlertCircle, Clock } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { Message } from "../types";
import { TypingIndicator } from "./TypingIndicator";

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const isStreaming = message.status === "streaming";
  const isError = message.status === "error";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm
          ${isUser
            ? "bg-sky-500/20 text-sky-400 border border-sky-500/30"
            : isError
            ? "bg-red-500/20 text-red-400 border border-red-500/30"
            : "bg-violet-500/20 text-violet-400 border border-violet-500/30"
          }`}
      >
        {isUser ? <User size={14} /> : isError ? <AlertCircle size={14} /> : <Bot size={14} />}
      </div>

      {/* Bubble */}
      <div className={`flex flex-col gap-1 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed
            ${isUser
              ? "bg-sky-600 text-white rounded-tr-sm"
              : isError
              ? "bg-red-500/10 border border-red-500/20 text-red-300 rounded-tl-sm"
              : "bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-sm"
            }`}
        >
          {isStreaming && !message.content ? (
            <TypingIndicator />
          ) : isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
              {isStreaming && (
                <motion.span
                  className="inline-block w-0.5 h-4 bg-sky-400 ml-0.5 align-middle"
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity }}
                />
              )}
            </div>
          )}
        </div>

        {/* Meta */}
        <div className="flex items-center gap-2 text-xs text-slate-500 px-1">
          <span>{formatDistanceToNow(message.timestamp, { addSuffix: true })}</span>
          {message.duration_ms !== undefined && message.duration_ms > 0 && (
            <>
              <span>·</span>
              <span className="flex items-center gap-0.5">
                <Clock size={10} />
                {(message.duration_ms / 1000).toFixed(1)}s
              </span>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
}
