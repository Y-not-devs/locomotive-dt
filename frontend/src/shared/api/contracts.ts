import type { AlertItem } from "@/entities/alert/model/types";
import type { HealthIndexSnapshot } from "@/entities/health-index/model/types";
import type { RouteState } from "@/entities/route/model/types";
import type { TelemetryPoint } from "@/entities/telemetry/model/types";

export interface LiveDashboardState {
  online: boolean;
  replayAvailableMinutes: number;
  telemetry: TelemetryPoint;
  health: HealthIndexSnapshot;
  alerts: AlertItem[];
  route: RouteState;
}
