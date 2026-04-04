export type HealthCategory = "normal" | "warning" | "critical";

export interface HealthFactor {
  key: string;
  label: string;
  weight: number;
  normalizedValue: number;
  contribution: number;
}

export interface HealthIndexSnapshot {
  score: number;
  category: HealthCategory;
  topFactors: HealthFactor[];
}
