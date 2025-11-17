class Inverter:
    """Inverter model."""

    def __init__(self, peak_efficiency=0.98):
        self.peak_efficiency = peak_efficiency

    def convert_dc_to_ac(self, p_dc_kw):
        if p_dc_kw <= 0:
            return 0.0, 0.0
        load_frac = min(1.0, p_dc_kw / 150.0)
        eff = self.peak_efficiency - 0.02 * (1.0 - (1.0 - load_frac) ** 2)
        eff = max(0.85, min(self.peak_efficiency, eff))
        p_ac_kw = p_dc_kw * eff
        return p_ac_kw, eff

    def convert_ac_to_dc(self, p_ac_kw):
        if p_ac_kw <= 0:
            return 0.0, 0.0
        eff = self.peak_efficiency - 0.03
        eff = max(0.7, eff)
        p_dc_kw = p_ac_kw * eff
        return p_dc_kw, eff

    def info(self):
        return {"peak_efficiency": self.peak_efficiency}
