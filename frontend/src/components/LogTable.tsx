import type { Log } from "../types";

const LEVEL_COLORS: Record<string, { bg: string; color: string }> = {
  INFO:  { bg: "#e8f4fd", color: "#1a5f8a" },
  WARN:  { bg: "#fff8e1", color: "#8a6000" },
  ERROR: { bg: "#fdecea", color: "#8a1a1a" },
};

interface Props {
  logs: Log[];
}

export default function LogTable({ logs }: Props) {
  if (logs.length === 0) {
    return (
      <p style={{ color: "#888", fontSize: "14px", textAlign: "center", marginTop: "40px" }}>
        No logs yet — waiting for data...
      </p>
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #eee", textAlign: "left" }}>
            <th style={{ padding: "8px 12px", color: "#555", fontWeight: 500 }}>Time</th>
            <th style={{ padding: "8px 12px", color: "#555", fontWeight: 500 }}>Service</th>
            <th style={{ padding: "8px 12px", color: "#555", fontWeight: 500 }}>Level</th>
            <th style={{ padding: "8px 12px", color: "#555", fontWeight: 500 }}>Message</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => {
            const colors = LEVEL_COLORS[log.level] ?? LEVEL_COLORS.INFO;
            return (
              <tr
                key={log.id}
                style={{ borderBottom: "1px solid #f0f0f0" }}
              >
                <td style={{ padding: "8px 12px", color: "#888", whiteSpace: "nowrap" }}>
                  {new Date(log.created_at).toLocaleTimeString()}
                </td>
                <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "#444" }}>
                  {log.service}
                </td>
                <td style={{ padding: "8px 12px" }}>
                  <span style={{
                    background: colors.bg,
                    color: colors.color,
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontWeight: 500,
                    fontSize: "11px",
                  }}>
                    {log.level}
                  </span>
                </td>
                <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "#333" }}>
                  {log.message}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}