import { useEffect, useState } from "react";

import { ConnectionStatusBanner } from "@/features/connection-status/ui/ConnectionStatusBanner";
import { ExportReportAction } from "@/features/export-report/ui/ExportReportAction";
import { ThresholdSettingsAction } from "@/features/threshold-settings/ui/ThresholdSettingsAction";
import { HealthOverviewWidget } from "@/widgets/health-overview/ui/HealthOverviewWidget";
import { ReplayTimelineWidget } from "@/widgets/replay-timeline/ui/ReplayTimelineWidget";
import { RouteMonitorWidget } from "@/widgets/route-monitor/ui/RouteMonitorWidget";
import { TelemetryGridWidget } from "@/widgets/telemetry-grid/ui/TelemetryGridWidget";
import { initialDashboardState, createNextMockState } from "@/shared/api/mock";
import { env } from "@/shared/config/env";
import { formatTimestamp } from "@/shared/lib/formatters";

export function CabinPage() {
  const [dashboard, setDashboard] = useState(initialDashboardState);

  useEffect(() => {
    const timerId = window.setInterval(() => {
      setDashboard((current) => createNextMockState(current));
    }, 1000);

    return () => {
      window.clearInterval(timerId);
    };
  }, []);

  return (
    <main className="dashboard-shell">
      <header className="dashboard-topbar">
        <div>
          <p className="eyebrow">Locomotive digital twin</p>
          <h1>Cabin dashboard</h1>
          <p className="subtle-copy">
            Live telemetry, explainable health score, route state, and replay entry points.
          </p>
        </div>

        <ConnectionStatusBanner
          online={dashboard.online}
          transport={`WebSocket ${env.wsUrl}`}
        />
      </header>

      <section className="dashboard-grid">
        <HealthOverviewWidget
          locomotiveId={dashboard.telemetry.locomotiveId}
          updatedAt={formatTimestamp(dashboard.telemetry.recordedAt)}
          health={dashboard.health}
        />

        <TelemetryGridWidget
          telemetry={dashboard.telemetry}
          alerts={dashboard.alerts}
        />

        <RouteMonitorWidget
          route={dashboard.route}
          telemetry={dashboard.telemetry}
        />

        <ReplayTimelineWidget
          replayAvailableMinutes={dashboard.replayAvailableMinutes}
          actions={
            <>
              <ThresholdSettingsAction />
              <ExportReportAction />
            </>
          }
        />
      </section>
    </main>
  );
}
