import os
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

def generate_plots(sim_results, output_dir="reports"):
    try:
        os.makedirs(output_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        print(f"Error: Could not create output directory '{output_dir}': {e}")
        return {}

    times = [r["time_min"] for r in sim_results]
    files = {}

    # define plots: key -> (ylabel, ydata (list or tuple of lists), labels tuple optional)
    plot_definitions = {
        "soc": ("Battery SOC (%)", [r["battery_soc_percent"] for r in sim_results], None),
        "speed": ("Speed (km/h)", [r["speed_kmph"] for r in sim_results], None),
        "power": ("Power (kW)", ([r["p_mech_kw"] for r in sim_results], [r.get("p_elec_kw", 0.0) for r in sim_results]), ("Mechanical", "Electrical")),
        "temp": ("Battery Temp (°C)", [r["battery_temp_c"] for r in sim_results], None),
    }

    for key, (ylabel, y_data, labels) in plot_definitions.items():
        plt.figure()
        if isinstance(y_data, tuple) or isinstance(y_data, list) and any(isinstance(x, list) for x in y_data):
            # two series (power)
            # ensure y_data is a tuple/list of two lists
            y0 = y_data[0]
            y1 = y_data[1]
            plt.plot(times, y0)
            plt.plot(times, y1)
            if labels:
                plt.legend(labels)
        else:
            plt.plot(times, y_data)

        plt.title(f"{ylabel.split('(')[0].strip()} vs Time")
        plt.xlabel("Time (min)")
        plt.ylabel(ylabel)
        plt.grid(True)

        file_path = os.path.join(output_dir, f"{key}_vs_time.png")
        try:
            plt.savefig(file_path, bbox_inches='tight', dpi=150)
            files[key] = file_path
        except (IOError, PermissionError) as e:
            print(f"Warning: Could not save plot '{file_path}'. Error: {e}")
            files[key] = None
        finally:
            plt.close()
    return files

def generate_pdf_report(sim_results, component_info, plot_files, filename="EV_Report.pdf"):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=12)

    # --- Cover Page ---
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Digital Twin - EV Powertrain Report", ln=True, align='C')
    pdf.ln(4)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(12)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6,
                   "This report contains simulation results from the EV digital twin, including component specs, summary metrics, and performance plots.")

    # --- System Components Section ---
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "System Components", ln=True)
    pdf.ln(4)
    for comp_name, comp_details in component_info.items():
        if isinstance(comp_details, dict):
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 6, comp_name.capitalize(), ln=True)
            pdf.set_font("Arial", size=10)
            for k, v in comp_details.items():
                pdf.cell(0, 5, f"  {k.replace('_', ' ').title()}: {v}", ln=True)
            pdf.ln(4)

    # --- Simulation Summary Section ---
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "Simulation Summary", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", size=10)
    if sim_results:
        final = sim_results[-1]
        initial = sim_results[0]
        total_distance = final["distance_km"]
        avg_consumption = 0.0
        if total_distance > 1e-6:
            energy_consumed = initial["battery_energy_kwh"] - final["battery_energy_kwh"]
            avg_consumption = energy_consumed / total_distance

        soc_drop = initial["battery_soc_percent"] - final["battery_soc_percent"]

        summary_text = (
            f"Total distance: {total_distance:.2f} km\n"
            f"Battery SOC drop: {soc_drop:.2f} %\n"
            f"Average consumption: {avg_consumption:.4f} kWh/km\n"
            f"Final battery SOC: {final['battery_soc_percent']:.2f} %\n"
            f"Final battery temperature: {final['battery_temp_c']:.2f} °C\n"
            f"Final battery health: {final['battery_health_percent']:.2f} %"
        )
        pdf.multi_cell(0, 6, summary_text)
    else:
        pdf.cell(0, 6, "No simulation results available.", ln=True)

    # --- Plots Section ---
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "Plots", ln=True)
    pdf.ln(4)
    for key in ("soc", "speed", "power", "temp"):
        path = plot_files.get(key)
        if path and os.path.exists(path):
            # scale to fit page width (approx 180 mm)
            pdf.image(path, w=180)
            pdf.ln(6)
        else:
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 6, f"(Plot for '{key}' could not be generated)", ln=True)

    # --- Save PDF ---
    try:
        pdf.output(filename)
        return filename
    except (IOError, PermissionError) as e:
        print(f"Error: Could not save PDF report to '{filename}'. Error: {e}")
        return None
