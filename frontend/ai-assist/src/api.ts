import axios from "axios";
import type { HealthStatus, ToolInfo } from "./types";

const BASE = "/api";

const http = axios.create({ baseURL: BASE, timeout: 120_000 });

export async function fetchHealth(): Promise<HealthStatus> {
  try {
    const { data } = await http.get("/health");
    return data as HealthStatus;
  } catch {
    return { status: "offline" };
  }
}

export async function fetchTools(): Promise<ToolInfo[]> {
  const { data } = await http.get("/tools");
  return data.tools as ToolInfo[];
}

export async function runQuery(
  query: string,
  onToken: (token: string) => void,
  onDone: (duration_ms: number) => void,
  onError: (msg: string) => void
): Promise<void> {
  const resp = await fetch(`${BASE}/run/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!resp.ok || !resp.body) {
    onError(`HTTP ${resp.status}`);
    return;
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      try {
        const event = JSON.parse(line.slice(6));
        if (event.type === "token") onToken(event.data);
        else if (event.type === "done") onDone(event.duration_ms ?? 0);
        else if (event.type === "error") onError(event.data);
      } catch {
        // ignore malformed lines
      }
    }
  }
}
