import type { AlertItem } from "@/entities/alert/model/types";
import type { TelemetryPoint } from "@/entities/telemetry/model/types";

interface TelemetryGridWidgetProps {
  telemetry: TelemetryPoint;
  alerts: AlertItem[];
}

const metricCards = [
  {
    key: "speed",
    label: "Speed",
    unit: "km/h",
    value: (telemetry: TelemetryPoint) => telemetry.speedKph.toFixed(1)
  },
  {
    key: "fuel",
    label: "Fuel reserve",
    unit: "%",
    value: (telemetry: TelemetryPoint) => telemetry.fuelLevelPct.toFixed(1)
  },
  {
    key: "pressure",
    label: "Brake pressure",
    unit: "bar",
    value: (telemetry: TelemetryPoint) => telemetry.brakePressureBar.toFixed(2)
  },
  {
    key: "temperature",
    label: "Engine temp",
    unit: "C",
    value: (telemetry: TelemetryPoint) => telemetry.engineTempC.toFixed(1)
  },
  {
    key: "electrical",
    label: "Battery",
    unit: "V",
    value: (telemetry: TelemetryPoint) => telemetry.batteryVoltageV.toFixed(1)
  },
  {
    key: "traction",
    label: "Traction current",
    unit: "A",
    value: (telemetry: TelemetryPoint) => telemetry.tractionCurrentA.toFixed(0)
  }
];

export function TelemetryGridWidget({
  telemetry,
  alerts
}: TelemetryGridWidgetProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Telemetry</p>
          <h2>Cockpit panels</h2>
        </div>
        <span className="subtle-copy">{alerts.length} active alerts</span>
      </div>

      <div className="metric-grid">
        {metricCards.map((card) => (
          <article className="metric-card" key={card.key}>
            <p>{card.label}</p>
            <strong>{card.value(telemetry)}</strong>
            <span>{card.unit}</span>
          </article>
        ))}
      </div>

      <div className="alert-stack">
        {alerts.length === 0 ? (
          <div className="empty-state">No active alerts in the current replay window.</div>
        ) : (
          alerts.map((alert) => (
            <article className={`alert-card severity-${alert.severity}`} key={alert.code}>
              <strong>{alert.code}</strong>
              <p>{alert.message}</p>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
