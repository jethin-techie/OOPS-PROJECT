# OOPS-PROJECT
A lightweight, educational digital twin of an EV powertrain implemented in Python. The project models the battery, motor (PMSM), inverter and transmission, composes them into an EVPowertrain that can be stepped through a simple drive cycle, and produces plots + a PDF simulation report. 

# EV Digital Twin (small modular refactor)

This repository contains a small EV powertrain digital twin split into modules for easier development and uploading to Git.

## Structure
- `ev_sim/components/` — battery, motor, inverter, transmission classes
- `ev_sim/powertrain.py` — EVPowertrain composition and step logic
- `ev_sim/drive_cycle.py` — drive cycle generator
- `ev_sim/reporting.py` — plots and PDF reporting
- `scripts/run_sim.py` — interactive runner; entrypoint for local simulation

## Quickstart
1. Create a virtual env and install deps:
   ```bash
   python -m venv venv
   source venv/bin/activate    # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
