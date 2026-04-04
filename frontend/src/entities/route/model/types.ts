export type TrackCurveKind = "straight" | "arcUp" | "arcDown";
export type RouteRestrictionSeverity = "warning" | "critical";

export interface RouteMapPoint {
  x: number;
  y: number;
}

export interface RouteTemplateOption {
  id: string;
  label: string;
  description: string;
}

export interface RouteSectionDraft {
  id: string;
  name: string;
  lengthKm: number;
  curve: TrackCurveKind;
  restricted: boolean;
  speedLimitKph?: number;
  stationName?: string;
}

export interface RouteSegmentState {
  id: string;
  name: string;
  startKm: number;
  endKm: number;
  restricted: boolean;
  speedLimitKph?: number;
  curve: TrackCurveKind;
  start: RouteMapPoint;
  end: RouteMapPoint;
  control1?: RouteMapPoint;
  control2?: RouteMapPoint;
  path: string;
}

export interface RouteStationState {
  id: string;
  name: string;
  km: number;
  segmentId: string;
  point: RouteMapPoint;
  angleDeg: number;
}

export interface RouteRestrictionState {
  id: string;
  label: string;
  km: number;
  segmentId: string;
  point: RouteMapPoint;
  severity: RouteRestrictionSeverity;
  speedLimitKph: number;
}

export interface RouteLocomotiveState {
  segmentId: string;
  progress: number;
  positionKm: number;
  headingDeg: number;
  point: RouteMapPoint;
}

export interface RouteViewportState {
  width: number;
  height: number;
  padding: number;
}

export interface RouteState {
  currentSection: string;
  activeTemplateId: string;
  templates: RouteTemplateOption[];
  draftSections: RouteSectionDraft[];
  segments: RouteSegmentState[];
  stations: RouteStationState[];
  restrictions: RouteRestrictionState[];
  locomotive: RouteLocomotiveState;
  viewport: RouteViewportState;
  totalDistanceKm: number;
}
