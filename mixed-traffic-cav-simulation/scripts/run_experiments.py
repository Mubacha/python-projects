#!/usr/bin/env python3
"""Run mixed HDV/CAV SUMO experiments at five CAV penetration rates."""

from __future__ import annotations

import argparse
import csv
import random
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VEHICLE_TYPES = PROJECT_ROOT / "config" / "vehicle_types.add.xml"
PENETRATION_RATES = (0, 25, 50, 75, 100)


def sumo_tools_dir() -> Path:
    """Locate SUMO's tools directory through SUMO_HOME."""
    import os

    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise EnvironmentError(
            "SUMO_HOME is not set. Set it to your SUMO installation directory."
        )
    tools_dir = Path(sumo_home) / "tools"
    if not tools_dir.is_dir():
        raise FileNotFoundError(f"SUMO tools directory not found: {tools_dir}")
    return tools_dir


def require_binary(name: str) -> str:
    binary = shutil.which(name)
    if not binary:
        raise FileNotFoundError(
            f"Could not find '{name}' on PATH. Add the SUMO bin directory to PATH."
        )
    return binary


def run_command(command: list[str], description: str) -> None:
    print(f"\n--- {description} ---")
    print(" ".join(command))
    subprocess.run(command, check=True)


def generate_base_trips(
    net_file: Path, trips_file: Path, duration: int, period: float, seed: int
) -> None:
    random_trips = sumo_tools_dir() / "randomTrips.py"
    command = [
        sys.executable,
        str(random_trips),
        "-n", str(net_file),
        "-o", str(trips_file),
        "--begin", "0",
        "--end", str(duration),
        "--period", str(period),
        "--seed", str(seed),
        "--min-distance", "200",
        "--validate",
        "--prefix", "veh",
    ]
    run_command(command, "Generating common trip demand")


def assign_vehicle_types(
    base_trips: Path, output_trips: Path, penetration: int, seed: int
) -> int:
    """Assign types using common seeded draws, so CAV assignments are nested."""
    tree = ET.parse(base_trips)
    root = tree.getroot()
    trip_elements = [element for element in root if element.tag in {"trip", "flow"}]
    rng = random.Random(seed)
    draws = [rng.random() for _ in trip_elements]

    cav_count = 0
    threshold = penetration / 100.0
    for element, draw in zip(trip_elements, draws):
        vehicle_type = "CAV" if draw < threshold else "HDV"
        element.set("type", vehicle_type)
        cav_count += vehicle_type == "CAV"

    output_trips.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_trips, encoding="UTF-8", xml_declaration=True)
    return cav_count


def parse_tripinfo(path: Path) -> dict[str, float]:
    tree = ET.parse(path)
    trips = tree.getroot().findall("tripinfo")
    if not trips:
        raise ValueError(
            f"No completed trips found in {path}. Check demand, routing, and simulation duration."
        )

    durations = [float(item.get("duration", 0)) for item in trips]
    waiting = [float(item.get("waitingTime", 0)) for item in trips]
    time_loss = [float(item.get("timeLoss", 0)) for item in trips]
    distances = [float(item.get("routeLength", 0)) for item in trips]
    speeds = [
        distance / duration * 3.6
        for distance, duration in zip(distances, durations)
        if duration > 0
    ]

    return {
        "completed_trips": len(trips),
        "mean_travel_time_s": sum(durations) / len(durations),
        "mean_waiting_time_s": sum(waiting) / len(waiting),
        "mean_time_loss_s": sum(time_loss) / len(time_loss),
        "mean_speed_kmh": sum(speeds) / len(speeds) if speeds else 0.0,
    }


def parse_emissions(path: Path, step_length: float) -> dict[str, float]:
    """Integrate per-step emission rates (mg/s) over simulation time."""
    totals_mg = {"CO2": 0.0, "fuel": 0.0, "NOx": 0.0}
    tree = ET.parse(path)

    for timestep in tree.getroot().iter("timestep"):
        for vehicle in timestep.findall("vehicle"):
            for attribute in totals_mg:
                value = vehicle.get(attribute)
                if value is not None:
                    try:
                        rate = float(value)
                    except ValueError:
                        continue
                    if rate >= 0:
                        totals_mg[attribute] += rate * step_length

    return {
        "total_co2_kg": totals_mg["CO2"] / 1_000_000,
        "total_fuel_kg": totals_mg["fuel"] / 1_000_000,
        "total_nox_kg": totals_mg["NOx"] / 1_000_000,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run SUMO experiments for 0/25/50/75/100 percent CAV penetration."
    )
    parser.add_argument("--net", required=True, help="Path to the exported SUMO .net.xml file")
    parser.add_argument("--duration", type=int, default=3600, help="Demand end time in seconds")
    parser.add_argument("--period", type=float, default=1.0, help="Mean trip insertion period in seconds")
    parser.add_argument("--step-length", type=float, default=0.1, help="SUMO simulation step length")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "results"))
    args = parser.parse_args()

    net_file = Path(args.net).expanduser().resolve()
    if not net_file.is_file():
        raise FileNotFoundError(f"Network file does not exist: {net_file}")
    if args.duration <= 0 or args.period <= 0 or args.step_length <= 0:
        parser.error("duration, period, and step-length must be positive")

    sumo = require_binary("sumo")
    duarouter = require_binary("duarouter")
    tools_dir = sumo_tools_dir()
    output_dir = Path(args.output_dir).expanduser().resolve()
    raw_dir = output_dir / "raw"
    work_dir = output_dir / "work"
    raw_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    base_trips = work_dir / "base.trips.xml"
    generate_base_trips(net_file, base_trips, args.duration, args.period, args.seed)

    summary_rows: list[dict[str, float | int]] = []
    for penetration in PENETRATION_RATES:
        scenario_name = f"cav_{penetration:03d}"
        scenario_dir = raw_dir / scenario_name
        scenario_dir.mkdir(parents=True, exist_ok=True)

        scenario_trips = work_dir / f"{scenario_name}.trips.xml"
        route_file = scenario_dir / "routes.rou.xml"
        tripinfo_file = scenario_dir / "tripinfo.xml"
        emissions_file = scenario_dir / "emission.xml"

        cav_count = assign_vehicle_types(
            base_trips, scenario_trips, penetration, args.seed
        )
        total_assigned = len(
            [node for node in ET.parse(scenario_trips).getroot() if node.tag in {"trip", "flow"}]
        )
        run_command(
            [
                sys.executable, str(tools_dir / "duarouter.py"),
                "-n", str(net_file),
                "-t", str(scenario_trips),
                "-o", str(route_file),
                "--additional-files", str(VEHICLE_TYPES),
                "--seed", str(args.seed),
            ],
            f"Routing {scenario_name}",
        )

        run_command(
            [
                sumo,
                "-n", str(net_file),
                "-r", str(route_file),
                "-a", str(VEHICLE_TYPES),
                "--begin", "0",
                "--end", str(args.duration + 1800),
                "--step-length", str(args.step_length),
                "--seed", str(args.seed),
                "--tripinfo-output", str(tripinfo_file),
                "--emission-output", str(emissions_file),
                "--device.emissions.probability", "1.0",
                "--duration-log.disable", "true",
                "--no-step-log", "true",
                "--waiting-time-memory", "1000",
            ],
            f"Simulating {penetration}% CAV penetration",
        )

        trip_metrics = parse_tripinfo(tripinfo_file)
        emission_metrics = parse_emissions(emissions_file, args.step_length)
        summary_rows.append(
            {
                "cav_penetration_percent": penetration,
                "assigned_trips": total_assigned,
                "assigned_cavs": cav_count,
                **trip_metrics,
                **emission_metrics,
            }
        )
        print(
            f"Completed {penetration}%: "
            f"{trip_metrics['completed_trips']} trips; "
            f"mean travel time {trip_metrics['mean_travel_time_s']:.1f} s"
        )

    summary_path = output_dir / "summary.csv"
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
    print(f"\nExperiment summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
