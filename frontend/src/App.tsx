import { useEffect, useState, useMemo } from "react";
import { supabase } from "./supabaseClient";
import type { Log, LogLevel } from "./types";
import LogTable from "./components/LogTable";
import FilterBar from "./components/FilterBar";

const MAX_LOGS = 500;

export default function App() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState<LogLevel | "ALL">("ALL");
  const [service, setService] = useState("ALL");

  useEffect(() => {
    supabase
      .from("logs")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(MAX_LOGS)
      .then(({ data }) => {
        if (data) setLogs(data as Log[]);
      });

    const channel = supabase
      .channel("logs-stream")
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "logs" },
        (payload) => {
          setLogs((prev) => {
            const updated = [payload.new as Log, ...prev];
            return updated.slice(0, MAX_LOGS);
          });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  const services = useMemo(() => {
    const unique = new Set(logs.map((l) => l.service));
    return Array.from(unique).sort();
  }, [logs]);

  const filtered = useMemo(() => {
    return logs.filter((log) => {
      if (level !== "ALL" && log.level !== level) return false;
      if (service !== "ALL" && log.service !== service) return false;
      if (search && !log.message.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [logs, level, service, search]);

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "32px 16px", fontFamily: "sans-serif" }}>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "22px", fontWeight: 600, margin: 0 }}>Logdash</h1>
        <p style={{ color: "#888", fontSize: "14px", margin: "4px 0 0" }}>
          {filtered.length} log{filtered.length !== 1 ? "s" : ""} — updates live
        </p>
      </div>
      <FilterBar
        search={search}
        onSearchChange={setSearch}
        level={level}
        onLevelChange={setLevel}
        service={service}
        onServiceChange={setService}
        services={services}
      />
      <LogTable logs={filtered} />
    </div>
  );
}