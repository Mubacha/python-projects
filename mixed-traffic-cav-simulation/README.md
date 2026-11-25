# Mixed-Traffic Simulation: CAV Penetration in a Kumasi Road Network

A reproducible SUMO/Python project for examining how different Connected and Automated Vehicle (CAV) penetration rates affect traffic operations and tailpipe emissions on an OpenStreetMap road network in Kumasi, Ghana.

## Research question

How do increasing CAV shares (0%, 25%, 50%, 75%, and 100%) affect travel time, waiting time, speed, CO2 emissions, and fuel consumption in a mixed-traffic simulation?

## Project status

**Stage 1 — project scaffold and experiment pipeline.** The scripts and configuration are provided here. The real Kumasi network must be generated locally with SUMO's OSM Web Wizard before experiments can be run. No simulation results are included or claimed yet.

## Tools

- [SUMO](https://sumo.dlr.de/) microscopic traffic simulator
- OpenStreetMap data via SUMO's `osmWebWizard.py`
- Python, pandas, and Matplotlib
- SUMO XML outputs: `tripinfo.xml` and `emission.xml`

## 1. Install and configure SUMO

Install SUMO and ensure that both the SUMO binaries and SUMO tools are available. Set the `SUMO_HOME` environment variable to the SUMO installation directory.

Typical Windows setup (adjust the version/path to your installation):

```powershell
$env:SUMO_HOME = "C:\\Program Files (x86)\\Eclipse\\Sumo"
$env:Path += ";$env:SUMO_HOME\\bin"
```

Typical Linux setup:

```bash
export SUMO_HOME="/usr/share/sumo"
export PATH="$SUMO_HOME/bin:$PATH"
```

Check that `sumo --version` works.

## 2. Export a real Kumasi road network from OpenStreetMap

Launch the OSM Web Wizard:

```bash
python "$SUMO_HOME/tools/osmWebWizard.py"
```

On Windows, run the equivalent command using your SUMO installation path, for example:

```powershell
python "$env:SUMO_HOME\\tools\\osmWebWizard.py"
```

In the wizard:

1. Navigate to **Kumasi, Ghana**.
2. Select a compact urban corridor around **Kejetia/Adum** or another clearly connected central Kumasi corridor.
3. Keep the selection modest (roughly a few kilometres across) so the first experiment runs on a manageable network.
4. Select passenger-car traffic and generate the SUMO scenario.
5. Save/export the generated network files into this project's `network/osm/` folder (create the folder first). At minimum, retain the generated `*.net.xml` network file.

The OSM Web Wizard can generate additional scenario files. The experiment script only requires the network file; it generates reproducible trips for each scenario.

**Important:** The precise road area is selected interactively in the wizard. Record the selected corridor, bounding box, and export date in your project notes after downloading it. Do not describe the network as generated until you have actually exported it.

OpenStreetMap data is © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the Open Database License (ODbL). Retain attribution when redistributing network data or maps.

## 3. Python environment

From this project directory:

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
pip install -r requirements.txt
```

## 4. Run the five penetration-rate experiments

After exporting the network, run:

```bash
python scripts/run_experiments.py --net network/osm/kumasi.net.xml
```

Replace the network path with the actual `*.net.xml` filename created by the wizard.

Optional settings:

```bash
python scripts/run_experiments.py \
  --net network/osm/kumasi.net.xml \
  --duration 3600 \
  --period 1.0 \
  --step-length 0.1 \
  --seed 42
```

The script creates the same demand pattern for each scenario and uses a seeded, nested assignment of CAVs. This helps isolate the effect of changing the CAV share. The five scenarios are 0%, 25%, 50%, 75%, and 100% CAVs.

For each scenario, the pipeline:
1. Generates a base set of trips using SUMO's `randomTrips.py`.
2. Assigns HDV/CAV vehicle types at the selected penetration rate.
3. Routes the trips with `duarouter`.
4. Runs SUMO and writes `tripinfo.xml` and `emission.xml`.
5. Extracts trip and emissions measures into a summary CSV.

Raw XML files are stored under `results/raw/`; aggregated results are written to `results/summary.csv`.

## 5. Generate comparison charts

After all five scenarios complete:

```bash
python scripts/plot_results.py
```

Charts are saved under `figures/`.

## Vehicle behaviour assumptions

| Parameter | Human-driven proxy | CAV proxy |
|---|---:|---:|
| Car-following model | Krauss | IDM |
| Desired headway (`tau`) | 1.5 s | 0.6 s |
| Maximum speed | 13.89 m/s | 13.89 m/s |
| Speed factor | 1.00 | 1.00 |
| Speed deviation | 0.10 | 0.00 |
| Minimum gap | 2.5 m | 2.5 m |

The CAV is represented with SUMO's Intelligent Driver Model (IDM), a shorter time headway, and lower speed variation. This is a **simplified automated-driving proxy**, not a full connected/cooperative driving implementation: it does not model V2V communication, platoon coordination, perception, or communication delays. The project deliberately starts with IDM because it is easier to reproduce and compare. A later extension could implement SUMO's CACC model and explicitly configure the required vehicle/device behaviour.

A 0.1-second simulation step is used to represent the shorter desired headway more consistently. SUMO's safety constraints may still prevent vehicles from maintaining the desired headway in every situation.

## Measures and interpretation

- **Mean travel time:** average trip duration (s).
- **Mean waiting time:** average time spent waiting (s).
- **Mean speed:** average trip distance divided by trip duration (km/h).
- **Total CO2:** integrated SUMO emission rate across recorded simulation steps (kg).
- **Total fuel:** integrated SUMO fuel rate (kg).

Emissions are aggregated from SUMO's per-step emission rates using the simulation step length. Emission totals should be compared alongside the number of completed trips and demand served; a scenario with fewer completed trips may appear to emit less simply because fewer vehicles finished.

## Reproducibility and limitations

- The same base trip list and random seed are used across penetration rates.
- The CAV assignment is nested: vehicles assigned as CAVs at a lower penetration remain CAVs at higher penetration rates.
- This is a single-run exploratory experiment. For stronger research conclusions, repeat each penetration rate over multiple random seeds and report means and variability.
- Results depend on the selected network, demand, simulation duration, warm-up, routing success, and SUMO version.
- The first version does not calibrate demand to observed Kumasi traffic counts. Treat results as a controlled simulation exercise, not a validated prediction of real-world traffic conditions.

## Suggested next steps

1. Export and document the Kumasi corridor.
2. Run a baseline experiment and check trip completion and congestion.
3. Repeat experiments over multiple seeds.
4. Calibrate traffic demand using observed counts if suitable data become available.
5. Compare the IDM CAV proxy with a properly configured CACC scenario.

## Citation

If you use SUMO, cite the SUMO project and its documentation. Attribute OpenStreetMap data as described above.
