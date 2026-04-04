export type AlertSeverity = "info" | "warning" | "critical";

export interface AlertItem {
  code: string;
  severity: AlertSeverity;
  message: string;
  sourceMetric?: string;
}
