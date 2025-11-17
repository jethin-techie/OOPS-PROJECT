import math

class Transmission:
    """Transmission model."""

    def __init__(self, gear_ratios=None, final_drive=9.0, wheel_radius_m=0.3):
        if gear_ratios is None:
            gear_ratios = [3.6, 2.1, 1.4, 1.0, 0.8]
        self.gear_ratios = gear_ratios
        self.current_gear = 1
        self.final_drive = final_drive
        self.wheel_radius_m = wheel_radius_m

    def get_total_ratio(self):
        return self.gear_ratios[self.current_gear - 1] * self.final_drive

    def wheel_speed_rpm_to_motor_rpm(self, wheel_speed_kmph):
        wheel_speed_mps = wheel_speed_kmph * 1000.0 / 3600.0
        wheel_rps = wheel_speed_mps / (2.0 * math.pi * self.wheel_radius_m)
        motor_rps = wheel_rps * self.get_total_ratio()
        return motor_rps * 60.0

    def info(self):
        return {"gear_ratios": self.gear_ratios, "current_gear": self.current_gear}
