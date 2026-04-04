export interface RouteSectionState {
  name: string;
  startKm: number;
  endKm: number;
  restricted: boolean;
}

export interface RouteState {
  currentSection: string;
  sections: RouteSectionState[];
}
