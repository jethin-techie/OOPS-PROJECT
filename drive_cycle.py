def create_simple_drive_cycle(duration_min=30, dt_min=0.5, avg_speed_kmph=60.0):
    low_cruise_speed = avg_speed_kmph * 0.85
    high_cruise_speed = avg_speed_kmph * 1.25
    steps = int(duration_min / dt_min)
    speeds = []
    for i in range(steps):
        t = i * dt_min
        if t < 2:
            speeds.append(0.0)
        elif t < 6:
            speeds.append((t - 2) / 4.0 * low_cruise_speed)
        elif t < 16:
            speeds.append(low_cruise_speed)
        elif t < 20:
            speeds.append(low_cruise_speed + (t - 16) / 4.0 * (high_cruise_speed - low_cruise_speed))
        elif t < 26:
            speeds.append(high_cruise_speed)
        elif t < 28:
            speeds.append(high_cruise_speed - (t - 26) / 2.0 * high_cruise_speed)
        else:
            speeds.append(0.0)
    return speeds
