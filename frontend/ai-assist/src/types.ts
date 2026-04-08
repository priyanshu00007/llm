export type Role = "user" | "assistant" | "system";
export type MessageStatus = "sending" | "streaming" | "done" | "error";

export interface Message {
  id: string;
  role: Role;
  content: string;
  status: MessageStatus;
  timestamp: Date;
  duration_ms?: number;
}

export interface ToolInfo {
  name: string;
  description: string;
}

export interface HealthStatus {
  status: "healthy" | "degraded" | "offline";
  provider?: string;
  tools?: number;
}
