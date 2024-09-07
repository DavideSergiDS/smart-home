export class TelemetrySource {
  constructor(readonly target: TelemetryTarget) {}

  public *start(): Generator<TelemetrySample> {
    const t = this.target;
    yield {
      value: Math.random() * 100,
      telemetryId: "temp",
      targetId: t.id,
      label: "Temperature",
      unit: "°C",
    };
  }

  public async stop(): Promise<void> {}
}

export interface TelemetrySample {
  targetId: string;
  telemetryId: string;
  label: string;
  unit: string;
  value: number | { [dim: string]: number };
}

export interface TelemetryTarget {
  id: string;
  label: string;
  description: string;
  metadata?: unknown;
}

export async function getTelemetryTargets(): Promise<TelemetryTarget[]> {
  return [
    {
      id: "kitchen-1",
      label: "Kitchen",
      description: "Kitchen placed at 1st floor in front of the backyard.",
    },
    {
      id: "backyard-1",
      label: "Backyard",
      description: "Backyard with fruit trees and ducks.",
    },
    {
      id: "bathroom-1",
      label: "Blue bathroom",
      description: "Smallest bathroom placed nearby the kitchen.",
    },
    {
      id: "bathroom-2",
      label: "Green bathroom",
      description: "Biggest bathroom placed nearby the bedroom.",
    },
  ];
}
