import type { Dispatch, SetStateAction } from "react";
import { useState } from "react";

import type { RouteSectionDraft, RouteState, TrackCurveKind } from "@/entities/route/model/types";
import type { TelemetryPoint } from "@/entities/telemetry/model/types";
import {
  buildRouteState,
  createEmptyDraftSection,
  getTemplateDraftSections
} from "@/services/track-map/trackMapBuilder";

interface RouteMonitorWidgetProps {
  route: RouteState;
  telemetry: TelemetryPoint;
}

export function RouteMonitorWidget({
  route,
  telemetry
}: RouteMonitorWidgetProps) {
  const [activeTemplateId, setActiveTemplateId] = useState(route.activeTemplateId);
  const [draftSections, setDraftSections] = useState(() =>
    route.draftSections.map((section) => ({ ...section }))
  );
  const [zoom, setZoom] = useState(1);
  const [selectedSegmentId, setSelectedSegmentId] = useState<string | null>(null);

  const displayedRoute = buildRouteState({
    templateId: activeTemplateId,
    draftSections,
    positionKm: telemetry.positionKm
  });
  const focusedSegment =
    displayedRoute.segments.find((segment) => segment.id === selectedSegmentId) ??
    displayedRoute.segments.find((segment) => segment.id === displayedRoute.locomotive.segmentId) ??
    displayedRoute.segments[0];

  return (
    <section className="panel route-monitor-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Interactive route map</p>
          <h2>{displayedRoute.currentSection}</h2>
        </div>
        <div className="route-monitor-stats">
          <span className="subtle-copy">
            {telemetry.positionKm.toFixed(1)} / {displayedRoute.totalDistanceKm.toFixed(1)} km
          </span>
          <span className="subtle-copy">{displayedRoute.currentSection}</span>
        </div>
      </div>

      <div className="track-map-toolbar">
        <div className="template-chip-row">
          {displayedRoute.templates.map((template) => (
            <button
              className={`template-chip ${template.id === activeTemplateId ? "is-active" : ""}`}
              key={template.id}
              onClick={() => {
                setActiveTemplateId(template.id);
                setDraftSections(getTemplateDraftSections(template.id));
                setSelectedSegmentId(null);
              }}
              type="button"
            >
              {template.label}
            </button>
          ))}
        </div>

        <label className="zoom-control">
          <span>Zoom</span>
          <input
            max={1.5}
            min={0.7}
            onChange={(event) => setZoom(Number(event.target.value))}
            step={0.1}
            type="range"
            value={zoom}
          />
        </label>
      </div>

      <div className="track-map-stage">
        <svg
          className="track-map-svg"
          style={{ transform: `scale(${zoom})` }}
          viewBox={`0 0 ${displayedRoute.viewport.width} ${displayedRoute.viewport.height}`}
        >
          <defs>
            <linearGradient id="trackRailGradient" x1="0%" x2="100%" y1="0%" y2="0%">
              <stop offset="0%" stopColor="rgba(56, 209, 197, 0.5)" />
              <stop offset="100%" stopColor="rgba(120, 164, 191, 0.85)" />
            </linearGradient>
            <filter height="160%" id="trainGlow" width="160%" x="-30%" y="-30%">
              <feDropShadow dx="0" dy="0" floodColor="#38d1c5" floodOpacity="0.35" stdDeviation="6" />
            </filter>
          </defs>

          {displayedRoute.segments.map((segment) => {
            const isActive = segment.id === displayedRoute.locomotive.segmentId;
            const isFocused = segment.id === focusedSegment.id;

            return (
              <g
                className="track-segment-group"
                key={segment.id}
                onClick={() => setSelectedSegmentId(segment.id)}
              >
                <path className="track-sleeper" d={segment.path} />
                <path
                  className={`track-rail ${isActive ? "is-active" : ""} ${segment.restricted ? "is-restricted" : ""} ${isFocused ? "is-focused" : ""}`}
                  d={segment.path}
                />
                <text
                  className="track-segment-label"
                  x={(segment.start.x + segment.end.x) / 2}
                  y={Math.min(segment.start.y, segment.end.y) - 20}
                >
                  {segment.name}
                </text>
              </g>
            );
          })}

          {displayedRoute.stations.map((station) => (
            <g className="track-station-marker" key={station.id}>
              <circle cx={station.point.x} cy={station.point.y} r={10} />
              <text x={station.point.x} y={station.point.y - 16}>
                {station.name}
              </text>
            </g>
          ))}

          {displayedRoute.restrictions.map((restriction) => (
            <g className={`track-restriction-marker severity-${restriction.severity}`} key={restriction.id}>
              <rect
                height={22}
                rx={6}
                width={46}
                x={restriction.point.x - 23}
                y={restriction.point.y - 54}
              />
              <text x={restriction.point.x} y={restriction.point.y - 39}>
                {restriction.speedLimitKph}
              </text>
              <line
                x1={restriction.point.x}
                x2={restriction.point.x}
                y1={restriction.point.y - 12}
                y2={restriction.point.y - 28}
              />
            </g>
          ))}

          <g
            className="track-locomotive-marker"
            filter="url(#trainGlow)"
            transform={`translate(${displayedRoute.locomotive.point.x} ${displayedRoute.locomotive.point.y}) rotate(${displayedRoute.locomotive.headingDeg})`}
          >
            <circle className="track-locomotive-pulse" cx={0} cy={0} r={14} />
            <path d="M -15 -9 L 16 0 L -15 9 Z" />
          </g>
        </svg>
      </div>

      <div className="route-monitor-summary">
        <div className="route-summary-card">
          <p className="eyebrow">Focused segment</p>
          <strong>{focusedSegment.name}</strong>
          <p className="subtle-copy">
            {focusedSegment.startKm.toFixed(1)}-{focusedSegment.endKm.toFixed(1)} km
          </p>
        </div>

        <div className="route-summary-card">
          <p className="eyebrow">Locomotive</p>
          <strong>{displayedRoute.locomotive.positionKm.toFixed(1)} km</strong>
          <p className="subtle-copy">
            Heading {displayedRoute.locomotive.headingDeg.toFixed(0)} deg
          </p>
        </div>

        <div className="route-summary-card">
          <p className="eyebrow">Restrictions</p>
          <strong>{displayedRoute.restrictions.length}</strong>
          <p className="subtle-copy">
            {displayedRoute.stations.length} stations in current design
          </p>
        </div>
      </div>

      <div className="track-builder">
        <div className="track-builder-header">
          <div>
            <p className="eyebrow">Route constructor</p>
            <h3>Configure the track schema</h3>
          </div>
          <button
            className="ghost-button"
            onClick={() =>
              setDraftSections((current) => [...current, createEmptyDraftSection(current.length)])
            }
            type="button"
          >
            Add section
          </button>
        </div>

        <div className="track-builder-list">
          {draftSections.map((section, index) => (
            <article className="track-builder-card" key={section.id}>
              <div className="track-builder-grid">
                <label>
                  <span>Name</span>
                  <input
                    onChange={(event) =>
                      updateSection(setDraftSections, index, { name: event.target.value })
                    }
                    type="text"
                    value={section.name}
                  />
                </label>

                <label>
                  <span>Length, km</span>
                  <input
                    min={1}
                    onChange={(event) =>
                      updateSection(setDraftSections, index, {
                        lengthKm: Math.max(1, Number(event.target.value) || 1)
                      })
                    }
                    type="number"
                    value={section.lengthKm}
                  />
                </label>

                <label>
                  <span>Curve</span>
                  <select
                    onChange={(event) =>
                      updateSection(setDraftSections, index, {
                        curve: event.target.value as TrackCurveKind
                      })
                    }
                    value={section.curve}
                  >
                    <option value="straight">Straight</option>
                    <option value="arcUp">Arc up</option>
                    <option value="arcDown">Arc down</option>
                  </select>
                </label>

                <label>
                  <span>Station</span>
                  <input
                    onChange={(event) =>
                      updateSection(setDraftSections, index, {
                        stationName: event.target.value
                      })
                    }
                    placeholder="Optional"
                    type="text"
                    value={section.stationName ?? ""}
                  />
                </label>

                <label>
                  <span>Speed limit</span>
                  <input
                    min={10}
                    onChange={(event) =>
                      updateSection(setDraftSections, index, {
                        speedLimitKph: event.target.value ? Number(event.target.value) : undefined
                      })
                    }
                    placeholder="Optional"
                    type="number"
                    value={section.speedLimitKph ?? ""}
                  />
                </label>

                <label className="checkbox-field">
                  <input
                    checked={section.restricted}
                    onChange={(event) =>
                      updateSection(setDraftSections, index, {
                        restricted: event.target.checked
                      })
                    }
                    type="checkbox"
                  />
                  <span>Restricted segment</span>
                </label>
              </div>

              <div className="track-builder-actions">
                <button
                  className="ghost-button"
                  onClick={() => setSelectedSegmentId(section.id)}
                  type="button"
                >
                  Focus on map
                </button>
                <button
                  className="ghost-button danger-outline"
                  disabled={draftSections.length === 1}
                  onClick={() =>
                    setDraftSections((current) => current.filter((_, sectionIndex) => sectionIndex !== index))
                  }
                  type="button"
                >
                  Remove
                </button>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function updateSection(
  setDraftSections: Dispatch<SetStateAction<RouteSectionDraft[]>>,
  index: number,
  patch: Partial<RouteSectionDraft>
) {
  setDraftSections((current) =>
    current.map((section, sectionIndex) =>
      sectionIndex === index ? { ...section, ...patch } : section
    )
  );
}
