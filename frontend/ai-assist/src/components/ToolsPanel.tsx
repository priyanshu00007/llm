import { motion, AnimatePresence } from "framer-motion";
import { X, Wrench } from "lucide-react";
import type { ToolInfo } from "../types";

interface Props {
  tools: ToolInfo[];
  open: boolean;
  onClose: () => void;
}

const TOOL_ICONS: Record<string, string> = {
  calculator: "🧮",
  send_email: "📧",
  get_weather: "🌤️",
  get_weather_no_api: "🌦️",
  write_file: "📝",
  read_file: "📂",
  get_current_time: "🕐",
  scrape_webpage: "🌐",
  make_api_request: "🔌",
  query_database: "🗄️",
  analyze_csv: "📊",
  search_web: "🔍",
  crawl_website: "🕷️",
  get_latest_news: "📰",
  get_stock_price_no_api: "📈",
  extract_product_details: "🛒",
  extract_faq_from_page: "❓",
};

export function ToolsPanel({ tools, open, onClose }: Props) {
  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-80 bg-slate-900 border-l border-slate-700 z-50 flex flex-col"
          >
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
              <div className="flex items-center gap-2 text-slate-200 font-semibold">
                <Wrench size={16} className="text-sky-400" />
                Tools ({tools.length})
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
                aria-label="Close tools panel"
              >
                <X size={16} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {tools.map((tool) => (
                <div
                  key={tool.name}
                  className="p-3 rounded-xl bg-slate-800 border border-slate-700 hover:border-slate-600 transition-colors"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-base">{TOOL_ICONS[tool.name] ?? "🔧"}</span>
                    <span className="text-sm font-medium text-slate-200 font-mono">
                      {tool.name}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                    {tool.description}
                  </p>
                </div>
              ))}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
