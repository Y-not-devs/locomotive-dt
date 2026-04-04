import type { ReactNode } from "react";

interface ReplayTimelineWidgetProps {
  replayAvailableMinutes: number;
  actions: ReactNode;
}

export function ReplayTimelineWidget({
  replayAvailableMinutes,
  actions
}: ReplayTimelineWidgetProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Replay and report</p>
          <h2>{replayAvailableMinutes} minute window</h2>
        </div>
      </div>

      <div className="timeline-card">
        <label htmlFor="replay-window">Replay focus</label>
        <input
          id="replay-window"
          className="timeline-slider"
          type="range"
          min={1}
          max={replayAvailableMinutes}
          defaultValue={5}
        />
        <p className="subtle-copy">
          The initial skeleton reserves the interaction surface for replay, event marks, and CSV or PDF export.
        </p>
      </div>

      <div className="action-row">{actions}</div>
    </section>
  );
}
