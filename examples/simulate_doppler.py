import numpy as np
import matplotlib.pyplot as plt
from shannon.orbits import PassPredictor
from shannon.ground_station import GroundStation
from shannon.utils import SPEED_OF_LIGHT

# Define KTH Ground Station (Stockholm)
kth_station = GroundStation(lat=59.3498, lon=18.0707, alt=10)

# Load TLE for NOAA-19
tle_line1 = "1 33591U 09005A   20265.56828552  .00000055  00000-0  57632-4 0  9995"
tle_line2 = "2 33591  99.1989 123.6338 0013952 147.2885 212.9238 14.12351659595519"
predictor = PassPredictor(tle_line1=tle_line1, tle_line2=tle_line2)

# Get next pass
pass_data = predictor.get_next_pass(kth_station)

if pass_data:
    print(f"Pass found: {pass_data.aos} to {pass_data.los}")

    # Calculate Doppler Shift
    # Delta f = - f * (v_r / c)
    # v_r is range rate (relative velocity in line of sight)
    # We can estimate v_r from change in range between points

    freq = 137.9125e6 # NOAA APT frequency

    times = [p['time'] for p in pass_data.points]
    ranges = [p['range_km'] * 1000 for p in pass_data.points] # meters

    # Calculate numerical derivative of range w.r.t time
    # Time delta is 30s (from orbits.py step)

    shifts = []

    for i in range(len(ranges)):
        if i == 0:
            dr = ranges[1] - ranges[0]
            dt = (times[1] - times[0]).total_seconds()
        elif i == len(ranges) - 1:
            dr = ranges[i] - ranges[i-1]
            dt = (times[i] - times[i-1]).total_seconds()
        else:
            dr = ranges[i+1] - ranges[i-1]
            dt = (times[i+1] - times[i-1]).total_seconds()

        v_r = dr / dt
        shift = - freq * (v_r / SPEED_OF_LIGHT)
        shifts.append(shift)

    # Plot S-Curve
    plt.figure(figsize=(10, 6))

    # Convert times to minutes from AOS
    minutes = [(t - pass_data.aos).total_seconds() / 60.0 for t in times]

    plt.plot(minutes, shifts)
    plt.title("Doppler Shift (S-Curve)")
    plt.xlabel("Time since AOS (min)")
    plt.ylabel("Frequency Shift (Hz)")
    plt.grid(True)
    plt.savefig("doppler_curve.png")
    print("Saved Doppler curve to doppler_curve.png")

else:
    print("No pass found in the next 24 hours.")
