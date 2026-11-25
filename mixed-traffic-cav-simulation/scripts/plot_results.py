#!/usr/bin/env python3
"""Create comparison plots from the aggregated SUMO experiment results."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_FILE = PROJECT_ROOT / "results" / "summary.csv"
FIGURES_DIR = PROJECT_ROOT / "figures"


def main() -> None:
    if not SUMMARY_FILE.is_file():
        raise FileNotFoundError(
            f"{SUMMARY_FILE} not found. Run scripts/run_experiments.py first."
        )

    data = pd.read_csv(SUMMARY_FILE).sort_values("cav_penetration_percent")
    if data.empty:
        raise ValueError("The summary file contains no experiment results.")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    x = data["cav_penetration_percent"]

    chart_specs = [
        ("mean_travel_time_s", "Mean travel time (s)", "mean_travel_time.png"),
        ("mean_waiting_time_s", "Mean waiting time (s)", "mean_waiting_time.png"),
        ("mean_speed_kmh", "Mean trip speed (km/h)", "mean_speed.png"),
        ("total_co2_kg", "Total CO2 emissions (kg)", "total_co2.png"),
        ("total_fuel_kg", "Total fuel consumption (kg)", "total_fuel.png"),
    ]

    for column, ylabel, filename in chart_specs:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(x, data[column], marker="o", linewidth=2)
        ax.set_xlabel("CAV penetration (%)")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{ylabel} vs. CAV penetration")
        ax.set_xticks(x)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        output_path = FIGURES_DIR / filename
        fig.savefig(output_path, dpi=300)
        plt.close(fig)
        print(f"Saved {output_path}")

    print("All comparison charts generated.")


if __name__ == "__main__":
    main()
