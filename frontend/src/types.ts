export type LogLevel = "INFO" | "WARN" | "ERROR";

export interface Log {
  id: string;
  created_at: string;
  service: string;
  level: LogLevel;
  message: string;
}
