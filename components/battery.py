import math

class Battery:
    """Battery model (kWh) with SOC, voltage, temperature, simple thermal model"""

    def __init__(self, capacity_kwh=50.0, nominal_voltage=400.0):
        if float(capacity_kwh) <= 0:
            raise ValueError("Battery capacity must be a positive number.")
        self._capacity_kwh = float(capacity_kwh)
        self._energy_kwh = float(capacity_kwh)
        self.nominal_voltage = float(nominal_voltage)
        self.temperature_c = 25.0
        self.health_percent = 100.0

    @property
    def capacity_kwh(self):
        return self._capacity_kwh

    @property
    def energy_kwh(self):
        return self._energy_kwh

    @property
    def soc_percent(self):
        return 100.0 * self._energy_kwh / self._capacity_kwh

    def discharge(self, energy_kwh):
        energy_kwh = max(0.0, energy_kwh)
        actual = min(self._energy_kwh, energy_kwh)
        self._energy_kwh -= actual
        # simple temp rise proportional to energy flow (heuristic)
        self.temperature_c += 0.02 * (actual * 1000.0 / max(1.0, (self.nominal_voltage / 100.0)))
        return actual

    def charge(self, energy_kwh):
        energy_kwh = max(0.0, energy_kwh)
        space = self._capacity_kwh - self._energy_kwh
        actual = min(space, energy_kwh)
        self._energy_kwh += actual
        self.temperature_c += 0.01 * (actual * 1000.0 / max(1.0, (self.nominal_voltage / 100.0)))
        return actual

    def update_health(self, cycles=0):
        self.health_percent -= 0.01 * cycles
        if self.temperature_c > 50:
            self.health_percent -= 0.02
        self.health_percent = max(0.0, min(100.0, self.health_percent))

    def info(self):
        return {
            "capacity_kwh": self._capacity_kwh,
            "energy_kwh": self._energy_kwh,
            "soc_percent": self.soc_percent,
            "temperature_c": self.temperature_c,
            "health_percent": self.health_percent
        }
