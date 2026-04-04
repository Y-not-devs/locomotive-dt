import type { HealthIndexSnapshot } from "@/entities/health-index/model/types";
import { formatCategory } from "@/shared/lib/formatters";

interface HealthOverviewWidgetProps {
  locomotiveId: string;
  updatedAt: string;
  health: HealthIndexSnapshot;
}

export function HealthOverviewWidget({
  locomotiveId,
  updatedAt,
  health
}: HealthOverviewWidgetProps) {
  return (
    <section className="panel panel-health">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Health index</p>
          <h2>{locomotiveId}</h2>
        </div>
        <span className={`status-chip status-${health.category}`}>
          {formatCategory(health.category)}
        </span>
      </div>

      <div className="health-score-wrap">
        <div className="health-score-ring">
          <strong>{health.score}</strong>
          <span>/100</span>
        </div>

        <div className="health-meta">
          <p>Updated {updatedAt}</p>
          <p>Transparent score based on live telemetry and alert penalties.</p>
        </div>
      </div>

      <div className="factor-list">
        {health.topFactors.map((factor) => (
          <article className="factor-card" key={factor.key}>
            <div>
              <strong>{factor.label}</strong>
              <p>Weight {factor.weight}</p>
            </div>
            <div className="factor-metrics">
              <span>Norm {Math.round(factor.normalizedValue * 100)}%</span>
              <span>Impact {factor.contribution.toFixed(1)}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
