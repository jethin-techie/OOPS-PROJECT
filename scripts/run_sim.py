#!/usr/bin/env python3
import os
from ev_sim.components import Battery, PMSM_Motor
from ev_sim.powertrain import EVPowertrain
from ev_sim.drive_cycle import create_simple_drive_cycle
from ev_sim.reporting import generate_plots, generate_pdf_report

def get_user_simulation_parameters():
    params = {}
    print("--- Configure EV Digital Twin Simulation ---")
    print("Press Enter to accept the default value shown in brackets.")

    def get_float_input(prompt, default, positive_only=False):
        while True:
            try:
                val_str = input(f"{prompt} (default: {default}): ")
                val = float(val_str) if val_str else default
                if positive_only and val <= 0:
                    print("Error: This value must be positive.")
                    continue
                return val
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    params['duration_min'] = get_float_input("Enter simulation duration (minutes)", 30.0, True)
    params['dt_min'] = get_float_input("Enter simulation time step (minutes)", 0.5, True)
    print("\n--- Drive Cycle Parameters ---")
    params['avg_speed_kmph'] = get_float_input("Enter target average cruising speed (km/h)", 60.0, True)
    print("\n--- Vehicle Parameters ---")
    params['mass_kg'] = get_float_input("Enter vehicle mass (kg)", 1750.0, True)
    print("\n--- Battery Parameters ---")
    params['capacity_kwh'] = get_float_input("Enter battery capacity (kWh)", 55.0, True)
    params['nominal_voltage'] = get_float_input("Enter battery nominal voltage (V)", 420.0, True)
    print("\n--- Motor Parameters ---")
    params['max_power_kw'] = get_float_input("Enter motor max power (kW)", 150.0, True)
    params['max_torque_nm'] = get_float_input("Enter motor max torque (Nm)", 350.0, True)

    print("\n--- Configuration complete. Starting simulation... ---")
    return params

def run_simulation(params, output_dir="reports"):
    try:
        battery = Battery(params['capacity_kwh'], params['nominal_voltage'])
        motor = PMSM_Motor(params['max_power_kw'], params['max_torque_nm'])
        ev = EVPowertrain(battery=battery, motor=motor, mass_kg=params['mass_kg'])
    except ValueError as e:
        print(f"Error: Could not initialize simulation components. {e}")
        return None, None, None

    drive_cycle = create_simple_drive_cycle(params['duration_min'], params['dt_min'], params['avg_speed_kmph'])
    sim_results = []
    print(f"Running simulation...")

    for sp in drive_cycle:
        metrics = ev.step(target_speed_kmph=sp, dt_min=params['dt_min'])
        sim_results.append(metrics)
        # Simple gear shifting logic
        if ev.speed_kmph > 70:
            ev.transmission.current_gear = min(len(ev.transmission.gear_ratios), ev.transmission.current_gear + 1)
        elif ev.speed_kmph < 30:
            ev.transmission.current_gear = max(1, ev.transmission.current_gear - 1)

    plot_files = generate_plots(sim_results, output_dir)
    comp_info = ev.info()
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "EV_Report.pdf")
    report_path = generate_pdf_report(sim_results, comp_info, plot_files, pdf_path)

    if report_path:
        print(f"Simulation complete. Report saved to: {report_path}")
    else:
        print("Simulation complete, but the PDF report could not be saved.")

    return sim_results, plot_files, report_path

if __name__ == "__main__":
    user_params = get_user_simulation_parameters()
    run_simulation(params=user_params, output_dir="reports")
