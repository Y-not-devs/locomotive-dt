export interface TelemetryPoint {
  locomotiveId: string;
  recordedAt: string;
  speedKph: number;
  fuelLevelPct: number;
  tractionCurrentA: number;
  batteryVoltageV: number;
  brakePressureBar: number;
  engineTempC: number;
  routeSection: string;
  positionKm: number;
}
