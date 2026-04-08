import { motion } from "framer-motion";
import type { HealthStatus } from "../types";

interface Props {
  health: HealthStatus;
}

export function StatusBadge({ health }: Props) {
  const colors: Record<string, string> = {
    healthy: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    degraded: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    offline: "bg-red-500/20 text-red-400 border-red-500/30",
  };

  const dots: Record<string, string> = {
    healthy: "bg-emerald-400",
    degraded: "bg-amber-400",
    offline: "bg-red-400",
  };

  const cls = colors[health.status] ?? colors.offline;
  const dot = dots[health.status] ?? dots.offline;

  return (
    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium ${cls}`}>
      <motion.span
        className={`w-1.5 h-1.5 rounded-full ${dot}`}
        animate={health.status === "healthy" ? { opacity: [1, 0.3, 1] } : {}}
        transition={{ duration: 2, repeat: Infinity }}
      />
      {health.status === "healthy"
        ? `${health.provider ?? "ready"} · ${health.tools ?? 0} tools`
        : health.status}
    </div>
  );
}
