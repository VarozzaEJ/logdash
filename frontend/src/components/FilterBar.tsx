import type { LogLevel } from "../types";

interface Props {
  service: string;
  onServiceChange: (value: string) => void;
  level: LogLevel | "ALL";
  onLevelChange: (value: LogLevel | "ALL") => void;
  search: string;
  onSearchChange: (value: string) => void;
  services: string[];
}

export default function FilterBar({
  service,
  onServiceChange,
  level,
  onLevelChange,
  search,
  onSearchChange,
  services,
}: Props) {
  return (
    <div style={{ display: "flex", gap: "12px", marginBottom: "16px", flexWrap: "wrap" }}>
      <input
        type="text"
        placeholder="Search messages..."
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        style={{ flex: 1, minWidth: "160px", padding: "6px 10px", borderRadius: "6px", border: "1px solid #ccc", fontSize: "13px" }}
      />
      <select
        value={service}
        onChange={(e) => onServiceChange(e.target.value)}
        style={{ padding: "6px 10px", borderRadius: "6px", border: "1px solid #ccc", fontSize: "13px" }}
      >
        <option value="ALL">All services</option>
        {services.map((s) => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      <select
        value={level}
        onChange={(e) => onLevelChange(e.target.value as LogLevel | "ALL")}
        style={{ padding: "6px 10px", borderRadius: "6px", border: "1px solid #ccc", fontSize: "13px" }}
      >
        <option value="ALL">All levels</option>
        <option value="INFO">INFO</option>
        <option value="WARN">WARN</option>
        <option value="ERROR">ERROR</option>
      </select>
    </div>
  );
}