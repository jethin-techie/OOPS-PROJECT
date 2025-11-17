import math

class Motor:
    """Base Motor class."""

    def __init__(self, max_power_kw=100.0, max_torque_nm=300.0, efficiency_map=None):
        self.max_power_kw = float(max_power_kw)
        self.max_torque_nm = float(max_torque_nm)
        self.speed_rpm = 0.0
        if efficiency_map is None:
            self.efficiency_map = lambda torque_frac, speed_frac: 0.85 + 0.10 * (1 - abs(torque_frac - 0.2))
        else:
            self.efficiency_map = efficiency_map

    def torque_to_power_kw(self, torque_nm, rpm):
        return (torque_nm * rpm * 2.0 * math.pi) / (60.0 * 1000.0)

    def get_efficiency(self, torque_nm, rpm):
        torque_frac = abs(torque_nm) / max(1e-6, self.max_torque_nm)
        speed_frac = min(1.0, rpm / 8000.0)
        eff = self.efficiency_map(torque_frac, speed_frac)
        return max(0.5, min(0.98, eff))

    def produce_power(self, torque_nm, rpm):
        p_shaft_kw = self.torque_to_power_kw(torque_nm, rpm)
        eff = self.get_efficiency(torque_nm, rpm)
        if eff <= 0:
            return 0.0, 0.0
        p_elec_kw = p_shaft_kw / eff
        p_elec_kw = min(p_elec_kw, self.max_power_kw)
        p_shaft_kw = p_elec_kw * eff
        return p_shaft_kw, p_elec_kw

    def regen_efficiency_fraction(self):
        return 0.5

    def info(self):
        return {"max_power_kw": self.max_power_kw, "max_torque_nm": self.max_torque_nm}


class PMSM_Motor(Motor):
    """Permanent Magnet Synchronous Motor subclass."""

    def __init__(self, max_power_kw=120.0, max_torque_nm=320.0):
        super().__init__(max_power_kw=max_power_kw, max_torque_nm=max_torque_nm)
        self.efficiency_map = lambda t, s: 0.9 - 0.1 * (t - 0.2) ** 2 - 0.05 * (s - 0.3) ** 2
