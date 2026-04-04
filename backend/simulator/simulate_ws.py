import argparse
import asyncio
import json
import random
import time
from typing import Dict, List

import websockets


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _drift(value: float, step: float, low: float, high: float) -> float:
    value += random.uniform(-step, step)
    return _clamp(value, low, high)


def _derive_alerts(state: Dict[str, float]) -> List[str]:
    alerts: List[str] = []
    if state["temp_engine"] > 108:
        alerts.append("engine_overheat")
    if state["temp_oil"] > 98:
        alerts.append("oil_overheat")
    if state["brake_pressure"] < 3.5:
        alerts.append("brake_pressure_low")
    if state["fuel_level"] < 3000:
        alerts.append("fuel_low")
    if state["voltage"] < 620 or state["voltage"] > 880:
        alerts.append("voltage_out_of_range")
    return alerts


def _build_payload(state: Dict[str, float]) -> Dict[str, object]:
    return {
        "timestamp": int(time.time()),
        "speed": round(state["speed"], 2),
        "traction_force": round(state["traction_force"], 2),
        "brake_pressure": round(state["brake_pressure"], 2),
        "fuel_level": round(state["fuel_level"], 2),
        "voltage": round(state["voltage"], 2),
        "current": round(state["current"], 2),
        "temp_oil": round(state["temp_oil"], 2),
        "temp_engine": round(state["temp_engine"], 2),
        "alerts": _derive_alerts(state),
    }


def _next_state(state: Dict[str, float]) -> Dict[str, float]:
    return {
        "speed": _drift(state["speed"], 6, 0, 120),
        "traction_force": _drift(state["traction_force"], 25, 0, 400),
        "brake_pressure": _drift(state["brake_pressure"], 0.3, 3, 8),
        "fuel_level": _drift(state["fuel_level"], 40, 2000, 10000),
        "voltage": _drift(state["voltage"], 20, 600, 900),
        "current": _drift(state["current"], 25, 100, 700),
        "temp_oil": _drift(state["temp_oil"], 2, 60, 110),
        "temp_engine": _drift(state["temp_engine"], 2, 70, 120),
    }


async def run_simulator(url: str, interval: float, burst: int, api_key: str) -> None:
    state = {
        "speed": 45.0,
        "traction_force": 120.0,
        "brake_pressure": 5.0,
        "fuel_level": 7200.0,
        "voltage": 760.0,
        "current": 260.0,
        "temp_oil": 78.0,
        "temp_engine": 82.0,
    }

    async with websockets.connect(
        url, extra_headers={"X-API-Key": api_key} if api_key else None
    ) as websocket:
        while True:
            for _ in range(max(1, burst)):
                payload = _build_payload(state)
                await websocket.send(json.dumps(payload))
                response = await websocket.recv()
                print(response)
                state = _next_state(state)
            await asyncio.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Telemetry WebSocket simulator")
    parser.add_argument("--url", default="ws://localhost:8000/ws/telemetry")
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--burst", type=int, default=1)
    parser.add_argument("--api-key", default="changeme")
    args = parser.parse_args()

    asyncio.run(run_simulator(args.url, args.interval, args.burst, args.api_key))


if __name__ == "__main__":
    main()
