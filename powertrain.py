import math
from .components.battery import Battery
from .components.motor import PMSM_Motor
from .components.inverter import Inverter
from .components.transmission import Transmission

class EVPowertrain:
    """EV system composed of all components."""

    def __init__(self, battery=None, motor=None, inverter=None, transmission=None, mass_kg=1700.0, crr=0.01, cda=0.7):
        self.battery = battery or Battery()
        self.motor = motor or PMSM_Motor()
        self.inverter = inverter or Inverter()
        self.transmission = transmission or Transmission()
        self.speed_kmph = 0.0
        self.distance_km = 0.0
        self.mass_kg = mass_kg
        self.crr = crr
        self.cda = cda
        self.time_minutes = 0.0

    def step(self, target_speed_kmph, dt_min=0.1):
        dt_h = dt_min / 60.0
        cur_v_mps = self.speed_kmph * 1000.0 / 3600.0
        tgt_v_mps = target_speed_kmph * 1000.0 / 3600.0
        dv = tgt_v_mps - cur_v_mps
        # limit acceleration (m/s^2)
        accel_mps2 = max(-3.0, min(2.0, dv / (dt_h * 3600.0) if dt_h > 0 else dv))
        new_v_mps = max(0.0, cur_v_mps + accel_mps2 * (dt_h * 3600.0))
        avg_v_mps = 0.5 * (cur_v_mps + new_v_mps)
        self.speed_kmph = avg_v_mps * 3.6
        delta_km = avg_v_mps * dt_h * 3600.0 / 1000.0
        self.distance_km += delta_km

        rho = 1.225
        f_aero = 0.5 * rho * self.cda * (avg_v_mps ** 2)
        f_roll = self.mass_kg * 9.81 * self.crr
        f_acc = self.mass_kg * accel_mps2
        f_total = f_aero + f_roll + f_acc
        if avg_v_mps < 0.1 and f_acc < 0:
            f_total = 0.0
        p_mech_kw = (f_total * avg_v_mps) / 1000.0

        torque_wheel_nm = f_total * self.transmission.wheel_radius_m
        torque_motor_nm = torque_wheel_nm / max(1e-6, self.transmission.get_total_ratio())
        motor_rpm = self.transmission.wheel_speed_rpm_to_motor_rpm(self.speed_kmph)

        p_shaft_kw = 0.0
        p_elec_kw = 0.0
        p_dc_kw = 0.0

        if p_mech_kw >= 0:
            p_shaft_kw, p_elec_kw = self.motor.produce_power(torque_motor_nm, motor_rpm)
            p_ac_kw, inv_eff = self.inverter.convert_dc_to_ac(p_elec_kw)
            # approximate DC power draw including inverter losses
            if inv_eff > 1e-6:
                p_dc_kw = p_elec_kw + (p_elec_kw * (1.0 / inv_eff - 1.0))
            else:
                p_dc_kw = p_elec_kw
            energy_needed_kwh = p_dc_kw * dt_h
            energy_drawn_kwh = self.battery.discharge(energy_needed_kwh)
            if energy_drawn_kwh < energy_needed_kwh and energy_needed_kwh > 0:
                shortage_frac = 1.0 - energy_drawn_kwh / energy_needed_kwh
                # reduce speed proportionally to shortage (heuristic)
                self.speed_kmph *= max(0.5, 1.0 - 0.8 * shortage_frac)
        else:
            # regen
            braking_power_kw = -p_mech_kw
            p_ac_regen_kw = braking_power_kw * self.motor.regen_efficiency_fraction()
            p_dc_regen_kw, inv_eff_regen = self.inverter.convert_ac_to_dc(p_ac_regen_kw)
            energy_regen_kwh = p_dc_regen_kw * dt_h
            actual_charged_kwh = self.battery.charge(energy_regen_kwh)
            p_shaft_kw, p_elec_kw = 0.0, -p_dc_regen_kw
            p_dc_kw = -actual_charged_kwh / dt_h if dt_h > 0 else 0.0

        # battery aging and thermal dynamics (simple)
        self.battery.update_health()
        ambient = 25.0
        self.battery.temperature_c += -0.1 * (self.battery.temperature_c - ambient) * dt_h * 60.0
        self.time_minutes += dt_min

        return {
            "time_min": self.time_minutes,
            "speed_kmph": self.speed_kmph,
            "distance_km": self.distance_km,
            "p_mech_kw": p_mech_kw,
            "p_motor_shaft_kw": p_shaft_kw,
            "p_elec_kw": p_elec_kw,
            "battery_energy_kwh": self.battery.energy_kwh,
            "battery_soc_percent": self.battery.soc_percent,
            "battery_temp_c": self.battery.temperature_c,
            "battery_health_percent": self.battery.health_percent,
            "motor_rpm": motor_rpm,
            "torque_motor_nm": torque_motor_nm,
            "transmission_gear": self.transmission.current_gear
        }

    def info(self):
        return {
            "battery": self.battery.info(),
            "motor": self.motor.info(),
            "inverter": self.inverter.info(),
            "transmission": self.transmission.info(),
            "mass_kg": self.mass_kg
        }
