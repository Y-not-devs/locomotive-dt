export function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}

export function formatCategory(value: "normal" | "warning" | "critical"): string {
  if (value === "normal") {
    return "Normal";
  }

  if (value === "warning") {
    return "Warning";
  }

  return "Critical";
}
