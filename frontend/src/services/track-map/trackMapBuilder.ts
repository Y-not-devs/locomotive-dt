import type {
  RouteLocomotiveState,
  RouteMapPoint,
  RouteRestrictionState,
  RouteSectionDraft,
  RouteSegmentState,
  RouteState,
  RouteStationState,
  RouteTemplateOption,
  TrackCurveKind
} from "@/entities/route/model/types";

interface BuildRouteStateParams {
  templateId: string;
  draftSections: RouteSectionDraft[];
  positionKm: number;
  currentSection?: string;
}

const templateCatalog: RouteTemplateOption[] = [
  {
    id: "mainline_demo",
    label: "Mainline Demo",
    description: "Balanced route with depot, bridge restriction, and terminal station."
  },
  {
    id: "cargo_loop",
    label: "Cargo Loop",
    description: "Compact switching route with short turns and dense station points."
  },
  {
    id: "mountain_pass",
    label: "Mountain Pass",
    description: "Longer route with alternating bends and multiple constrained sections."
  }
];

const templateSections: Record<string, RouteSectionDraft[]> = {
  mainline_demo: [
    { id: "depot", name: "Depot", lengthKm: 8, curve: "straight", restricted: false, stationName: "Depot" },
    { id: "north_yard", name: "North-Yard", lengthKm: 8, curve: "arcUp", restricted: false, stationName: "North Yard" },
    { id: "mainline_a", name: "Mainline-A", lengthKm: 18, curve: "straight", restricted: false },
    { id: "bridge", name: "Bridge", lengthKm: 8, curve: "arcDown", restricted: true, speedLimitKph: 40 },
    { id: "station_3", name: "Station-3", lengthKm: 6, curve: "straight", restricted: false, stationName: "Station 3" }
  ],
  cargo_loop: [
    { id: "yard_entry", name: "Yard Entry", lengthKm: 6, curve: "straight", restricted: false, stationName: "Gate" },
    { id: "cargo_curve", name: "Cargo Curve", lengthKm: 10, curve: "arcDown", restricted: true, speedLimitKph: 35 },
    { id: "loading_loop", name: "Loading Loop", lengthKm: 12, curve: "arcUp", restricted: false, stationName: "Cargo Bay" },
    { id: "exit_line", name: "Exit Line", lengthKm: 9, curve: "straight", restricted: false, stationName: "Dispatch" }
  ],
  mountain_pass: [
    { id: "valley_start", name: "Valley Start", lengthKm: 9, curve: "straight", restricted: false, stationName: "Valley" },
    { id: "ascent_a", name: "Ascent-A", lengthKm: 11, curve: "arcUp", restricted: true, speedLimitKph: 45 },
    { id: "ridge", name: "Ridge", lengthKm: 13, curve: "straight", restricted: false, stationName: "Ridge" },
    { id: "descent", name: "Descent", lengthKm: 12, curve: "arcDown", restricted: true, speedLimitKph: 30 },
    { id: "tunnel_terminal", name: "Tunnel Terminal", lengthKm: 7, curve: "straight", restricted: false, stationName: "Terminal" }
  ]
};

export function listRouteTemplates(): RouteTemplateOption[] {
  return templateCatalog.map((template) => ({ ...template }));
}

export function getTemplateDraftSections(templateId: string): RouteSectionDraft[] {
  const sections = templateSections[templateId] ?? templateSections.mainline_demo;
  return cloneDraftSections(sections);
}

export function cloneDraftSections(sections: RouteSectionDraft[]): RouteSectionDraft[] {
  return sections.map((section) => ({ ...section }));
}

export function createEmptyDraftSection(index: number): RouteSectionDraft {
  return {
    id: `custom_${index + 1}_${Math.random().toString(36).slice(2, 7)}`,
    name: `Section ${index + 1}`,
    lengthKm: 6,
    curve: index % 3 === 0 ? "straight" : index % 2 === 0 ? "arcDown" : "arcUp",
    restricted: false,
    stationName: ""
  };
}

export function buildRouteState({
  templateId,
  draftSections,
  positionKm,
  currentSection
}: BuildRouteStateParams): RouteState {
  const normalizedSections =
    draftSections.length > 0 ? cloneDraftSections(draftSections) : [createEmptyDraftSection(0)];
  const segments: RouteSegmentState[] = [];
  const stations: RouteStationState[] = [];
  const restrictions: RouteRestrictionState[] = [];

  let cursorX = 96;
  let baseY = 214;
  let kmCursor = 0;
  let minY = baseY;
  let maxY = baseY;

  normalizedSections.forEach((section) => {
    const lengthPx = Math.max(120, section.lengthKm * 20);
    const start = { x: cursorX, y: baseY };
    const end = { x: cursorX + lengthPx, y: baseY + curveOffset(section.curve) };
    const [control1, control2] = buildControls(start, end, section.curve);
    const path = buildSvgPath(start, end, control1, control2);
    const segment: RouteSegmentState = {
      id: section.id,
      name: section.name,
      startKm: round(kmCursor),
      endKm: round(kmCursor + section.lengthKm),
      restricted: section.restricted,
      speedLimitKph: section.speedLimitKph,
      curve: section.curve,
      start,
      end,
      control1,
      control2,
      path
    };

    segments.push(segment);

    if (section.stationName) {
      const station = pointOnSegment(segment, 0.52);
      stations.push({
        id: `${section.id}_station`,
        name: section.stationName,
        km: round(segment.startKm + section.lengthKm * 0.52),
        segmentId: segment.id,
        point: station.point,
        angleDeg: station.headingDeg
      });
    }

    if (section.restricted) {
      const restrictionPoint = pointOnSegment(segment, 0.72);
      restrictions.push({
        id: `${section.id}_restriction`,
        label: `${section.name} limit`,
        km: round(segment.startKm + section.lengthKm * 0.72),
        segmentId: segment.id,
        point: restrictionPoint.point,
        severity: (section.speedLimitKph ?? 40) <= 35 ? "critical" : "warning",
        speedLimitKph: section.speedLimitKph ?? 40
      });
    }

    cursorX = end.x + 76;
    baseY = end.y;
    kmCursor = segment.endKm;
    minY = Math.min(minY, start.y, end.y);
    maxY = Math.max(maxY, start.y, end.y);
  });

  const totalDistanceKm = round(kmCursor);
  const safePosition = normalizePosition(positionKm, totalDistanceKm);
  const activeSegment = locateSegment(segments, safePosition);
  const locomotive = buildLocomotiveState(activeSegment, safePosition);

  return {
    currentSection: currentSection ?? activeSegment.name,
    activeTemplateId: templateId,
    templates: listRouteTemplates(),
    draftSections: normalizedSections,
    segments,
    stations,
    restrictions,
    locomotive,
    viewport: {
      width: Math.max(960, Math.round(cursorX + 84)),
      height: Math.max(360, Math.round(maxY - minY + 180)),
      padding: 48
    },
    totalDistanceKm
  };
}

function buildLocomotiveState(
  activeSegment: RouteSegmentState,
  safePosition: number
): RouteLocomotiveState {
  const progress = segmentProgress(activeSegment, safePosition);
  const marker = pointOnSegment(activeSegment, progress);

  return {
    segmentId: activeSegment.id,
    progress,
    positionKm: safePosition,
    headingDeg: marker.headingDeg,
    point: marker.point
  };
}

function locateSegment(
  segments: RouteSegmentState[],
  positionKm: number
): RouteSegmentState {
  return (
    segments.find((segment) => segment.startKm <= positionKm && positionKm <= segment.endKm) ??
    segments[segments.length - 1]
  );
}

function segmentProgress(segment: RouteSegmentState, positionKm: number): number {
  const distance = Math.max(segment.endKm - segment.startKm, 0.001);
  return clamp((positionKm - segment.startKm) / distance, 0, 1);
}

function normalizePosition(positionKm: number, totalDistanceKm: number): number {
  if (totalDistanceKm <= 0) {
    return 0;
  }

  if (positionKm < 0) {
    return 0;
  }

  if (positionKm <= totalDistanceKm) {
    return round(positionKm);
  }

  return round(positionKm % totalDistanceKm);
}

function curveOffset(curve: TrackCurveKind): number {
  if (curve === "arcUp") {
    return -96;
  }

  if (curve === "arcDown") {
    return 96;
  }

  return 0;
}

function buildControls(
  start: RouteMapPoint,
  end: RouteMapPoint,
  curve: TrackCurveKind
): [RouteMapPoint | undefined, RouteMapPoint | undefined] {
  if (curve === "straight") {
    return [undefined, undefined];
  }

  const spanX = end.x - start.x;
  return [
    { x: start.x + spanX * 0.28, y: start.y },
    { x: start.x + spanX * 0.72, y: end.y }
  ];
}

function buildSvgPath(
  start: RouteMapPoint,
  end: RouteMapPoint,
  control1?: RouteMapPoint,
  control2?: RouteMapPoint
): string {
  if (!control1 || !control2) {
    return `M ${start.x.toFixed(1)} ${start.y.toFixed(1)} L ${end.x.toFixed(1)} ${end.y.toFixed(1)}`;
  }

  return [
    `M ${start.x.toFixed(1)} ${start.y.toFixed(1)}`,
    `C ${control1.x.toFixed(1)} ${control1.y.toFixed(1)}, ${control2.x.toFixed(1)} ${control2.y.toFixed(1)}, ${end.x.toFixed(1)} ${end.y.toFixed(1)}`
  ].join(" ");
}

function pointOnSegment(
  segment: RouteSegmentState,
  progress: number
): { point: RouteMapPoint; headingDeg: number } {
  const t = clamp(progress, 0, 1);
  const { start, end, control1, control2 } = segment;

  if (!control1 || !control2) {
    const x = start.x + (end.x - start.x) * t;
    const y = start.y + (end.y - start.y) * t;
    return {
      point: { x: round(x), y: round(y) },
      headingDeg: round((Math.atan2(end.y - start.y, end.x - start.x) * 180) / Math.PI)
    };
  }

  const x =
    (1 - t) ** 3 * start.x +
    3 * (1 - t) ** 2 * t * control1.x +
    3 * (1 - t) * t ** 2 * control2.x +
    t ** 3 * end.x;
  const y =
    (1 - t) ** 3 * start.y +
    3 * (1 - t) ** 2 * t * control1.y +
    3 * (1 - t) * t ** 2 * control2.y +
    t ** 3 * end.y;
  const dx =
    3 * (1 - t) ** 2 * (control1.x - start.x) +
    6 * (1 - t) * t * (control2.x - control1.x) +
    3 * t ** 2 * (end.x - control2.x);
  const dy =
    3 * (1 - t) ** 2 * (control1.y - start.y) +
    6 * (1 - t) * t * (control2.y - control1.y) +
    3 * t ** 2 * (end.y - control2.y);

  return {
    point: { x: round(x), y: round(y) },
    headingDeg: round((Math.atan2(dy, dx) * 180) / Math.PI)
  };
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function round(value: number): number {
  return Number(value.toFixed(3));
}
