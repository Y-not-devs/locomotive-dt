import type { LiveDashboardState } from "@/shared/api/contracts";
import type { RouteSectionState } from "@/entities/route/model/types";

const sections: RouteSectionState[] = [
  { name: "Depot", startKm: 0, endKm: 8, restricted: false },
  { name: "North-Yard", startKm: 8, endKm: 16, restricted: false },
  { name: "Mainline-A", startKm: 16, endKm: 34, restricted: false },
  { name: "Bridge", startKm: 34, endKm: 42, restricted: true },
  { name: "Station-3", startKm: 42, endKm: 48, restricted: false }
];

export const initialDashboardState: LiveDashboardState = {
  online: true,
  replayAvailableMinutes: 15,
  telemetry: {
    locomotiveId: "KZ-LOC-001",
    recordedAt: new Date().toISOString(),
    speedKph: 74,
    fuelLevelPct: 81,
    tractionCurrentA: 436,
    batteryVoltageV: 105,
    brakePressureBar: 6.2,
    engineTempC: 83,
    routeSection: "North-Yard",
    positionKm: 12.4
  },
  health: {
    score: 86,
    category: "normal",
    topFactors: [
      { key: "engine_temp_c", label: "Engine temperature", weight: 0.15, normalizedValue: 0.72, contribution: 4.2 },
      { key: "fuel_level_pct", label: "Fuel reserve", weight: 0.2, normalizedValue: 0.81, contribution: 3.8 },
      { key: "traction_current_a", label: "Traction current", weight: 0.15, normalizedValue: 0.74, contribution: 3.9 }
    ]
  },
  alerts: [
    { code: "MAINTENANCE_DUE", severity: "info", message: "Maintenance window in 2 operating hours." }
  ],
  route: {
    currentSection: "North-Yard",
    sections
  }
};

export function createNextMockState(previous: LiveDashboardState): LiveDashboardState {
  const nextSpeed = clamp(previous.telemetry.speedKph + jitter(6), 32, 108);
  const nextFuel = clamp(previous.telemetry.fuelLevelPct - Math.random() * 0.14, 10, 100);
  const nextTemp = clamp(previous.telemetry.engineTempC + jitter(2.8), 72, 97);
  const nextBrakePressure = clamp(previous.telemetry.brakePressureBar + jitter(0.35), 4.2, 6.8);
  const nextBattery = clamp(previous.telemetry.batteryVoltageV + jitter(1.2), 96, 110);
  const nextTractionCurrent = clamp(previous.telemetry.tractionCurrentA + jitter(26), 260, 590);
  const nextPosition = Number((previous.telemetry.positionKm + nextSpeed / 3600).toFixed(3));
  const nextSection =
    sections.find((section) => nextPosition >= section.startKm && nextPosition < section.endKm)?.name ??
    sections[sections.length - 1].name;

  const alerts =
    nextTemp > 92
      ? [{ code: "ENGINE_TEMP_HIGH", severity: "critical" as const, message: "Engine temperature is rising above the safe range." }]
      : nextFuel < 18
        ? [{ code: "FUEL_LOW", severity: "warning" as const, message: "Fuel reserve is below the warning threshold." }]
        : previous.alerts.filter((alert) => alert.severity === "info");

  const healthScore = Math.round(
    clamp(
      100 -
        (100 - nextFuel) * 0.14 -
        Math.max(nextTemp - 82, 0) * 1.7 -
        Math.max(5.5 - nextBrakePressure, 0) * 12 -
        alerts.length * 9,
      34,
      97
    )
  );

  return {
    ...previous,
    telemetry: {
      ...previous.telemetry,
      recordedAt: new Date().toISOString(),
      speedKph: Number(nextSpeed.toFixed(1)),
      fuelLevelPct: Number(nextFuel.toFixed(1)),
      tractionCurrentA: Number(nextTractionCurrent.toFixed(0)),
      batteryVoltageV: Number(nextBattery.toFixed(1)),
      brakePressureBar: Number(nextBrakePressure.toFixed(2)),
      engineTempC: Number(nextTemp.toFixed(1)),
      routeSection: nextSection,
      positionKm: nextPosition
    },
    health: {
      score: healthScore,
      category: healthScore >= 80 ? "normal" : healthScore >= 55 ? "warning" : "critical",
      topFactors: [
        { key: "engine_temp_c", label: "Engine temperature", weight: 0.15, normalizedValue: 0.72, contribution: Number(Math.max(nextTemp - 82, 0).toFixed(1)) },
        { key: "fuel_level_pct", label: "Fuel reserve", weight: 0.2, normalizedValue: Number((nextFuel / 100).toFixed(2)), contribution: Number(((100 - nextFuel) * 0.08).toFixed(1)) },
        { key: "brake_pressure_bar", label: "Brake pressure", weight: 0.2, normalizedValue: Number((nextBrakePressure / 7).toFixed(2)), contribution: Number(Math.max(5.5 - nextBrakePressure, 0).toFixed(1)) }
      ]
    },
    alerts,
    route: {
      ...previous.route,
      currentSection: nextSection
    }
  };
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function jitter(scale: number): number {
  return (Math.random() - 0.5) * scale;
}
