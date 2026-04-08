import { useRef, KeyboardEvent } from "react";
import TextareaAutosize from "react-textarea-autosize";
import { Send, Square } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  loading: boolean;
  disabled: boolean;
}

const SUGGESTIONS = [
  "What's the weather in Tokyo?",
  "Search the web for latest AI news",
  "Calculate 15% of 2847",
  "Get the current time and date",
  "What is the stock price of AAPL?",
];

export function ChatInput({ value, onChange, onSubmit, onStop, loading, disabled }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading && value.trim()) onSubmit();
    }
  };

  return (
    <div className="space-y-3">
      {/* Suggestions (only when empty) */}
      {!value && !loading && (
        <div className="flex flex-wrap gap-2 justify-center">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => { onChange(s); ref.current?.focus(); }}
              className="text-xs px-3 py-1.5 rounded-full bg-slate-800 border border-slate-700
                         text-slate-400 hover:text-slate-200 hover:border-slate-500 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input row */}
      <div className="flex items-end gap-2 bg-slate-800 border border-slate-700 rounded-2xl p-2
                      focus-within:border-sky-500/50 transition-colors">
        <TextareaAutosize
          ref={ref}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask the agent anything… (Shift+Enter for new line)"
          minRows={1}
          maxRows={8}
          disabled={disabled}
          className="flex-1 bg-transparent resize-none outline-none text-sm text-slate-200
                     placeholder:text-slate-500 px-2 py-1.5 leading-relaxed"
          aria-label="Message input"
        />

        <motion.button
          whileTap={{ scale: 0.92 }}
          onClick={loading ? onStop : onSubmit}
          disabled={!loading && (!value.trim() || disabled)}
          aria-label={loading ? "Stop generation" : "Send message"}
          className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-colors
            ${loading
              ? "bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30"
              : value.trim() && !disabled
              ? "bg-sky-600 text-white hover:bg-sky-500"
              : "bg-slate-700 text-slate-500 cursor-not-allowed"
            }`}
        >
          {loading ? <Square size={14} /> : <Send size={14} />}
        </motion.button>
      </div>

      <p className="text-center text-xs text-slate-600">
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
