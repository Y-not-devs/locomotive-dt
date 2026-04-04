import type { RouteState } from "@/entities/route/model/types";
import type { TelemetryPoint } from "@/entities/telemetry/model/types";

interface RouteMonitorWidgetProps {
  route: RouteState;
  telemetry: TelemetryPoint;
}

export function RouteMonitorWidget({
  route,
  telemetry
}: RouteMonitorWidgetProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Route monitor</p>
          <h2>{route.currentSection}</h2>
        </div>
        <span className="subtle-copy">{telemetry.positionKm.toFixed(1)} km</span>
      </div>

      <div className="route-track">
        {route.sections.map((section) => {
          const isActive = section.name === route.currentSection;
          return (
            <div
              className={`route-segment ${isActive ? "is-active" : ""} ${section.restricted ? "is-restricted" : ""}`}
              key={section.name}
            >
              <strong>{section.name}</strong>
              <span>
                {section.startKm}-{section.endKm} km
              </span>
            </div>
          );
        })}
      </div>

      <p className="subtle-copy">
        Current section and restrictions are shown here. Replace with Leaflet or MapLibre in the next iteration.
      </p>
    </section>
  );
}
