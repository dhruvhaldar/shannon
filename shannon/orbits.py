from sgp4.api import Satrec, jday
import numpy as np
import datetime
import matplotlib.pyplot as plt

class PassPredictor:
    def __init__(self, tle_line1, tle_line2):
        self.satellite = Satrec.twoline2rv(tle_line1, tle_line2)

    def get_next_pass(self, ground_station, start_time=None, max_duration_hours=24):
        """
        Calculates the next pass for the satellite over the ground station.
        """
        if start_time is None:
            start_time = datetime.datetime.utcnow()

        step_seconds = 30
        duration_seconds = int(max_duration_hours * 3600)
        num_steps = duration_seconds // step_seconds

        if num_steps <= 0:
            return None

        # Create time array
        times = [start_time + datetime.timedelta(seconds=step_seconds * i) for i in range(num_steps)]
        times_arr = np.array(times)

        # Calculate JD for SGP4
        # We need to extract components efficiently
        years = np.array([t.year for t in times])
        months = np.array([t.month for t in times])
        days = np.array([t.day for t in times])
        hours = np.array([t.hour for t in times])
        minutes = np.array([t.minute for t in times])
        seconds = np.array([t.second + t.microsecond * 1e-6 for t in times])

        jd_arr, fr_arr = jday(years, months, days, hours, minutes, seconds)

        # Vectorized SGP4 propagation
        e, r, v = self.satellite.sgp4_array(jd_arr, fr_arr)

        # Handle errors (e != 0)
        valid_sgp4 = (e == 0)

        # Vectorized look angles computation
        # Pass all points, filter later
        az, el, range_km = ground_station.compute_look_angles(r, times_arr)

        # Create mask for valid pass points:
        # 1. SGP4 was successful
        # 2. Elevation > 0
        mask = valid_sgp4 & (el > 0)

        if not np.any(mask):
            return None

        valid_indices = np.where(mask)[0]

        # Find the first continuous block of indices
        diff = np.diff(valid_indices)
        gaps = np.where(diff > 1)[0]

        if len(gaps) == 0:
            # Only one pass found in the window (or it's continuous)
            pass_indices = valid_indices
        else:
            # Multiple passes found, take the first one
            end_idx_in_valid = gaps[0]
            pass_indices = valid_indices[:end_idx_in_valid + 1]

        # Extract pass data
        aos_idx = pass_indices[0]
        los_idx = pass_indices[-1]

        aos = times[aos_idx]
        # Match iterative behavior: LOS is the time step *after* the last visible point
        # In the iterative loop, LOS was set when el <= 0.
        # Here los_idx is the last point where el > 0.
        # So the actual LOS event happens between times[los_idx] and times[los_idx+1].
        # The previous code returned the time of the first non-visible point.
        if los_idx + 1 < len(times):
            los = times[los_idx + 1]
        else:
             # If pass goes to the end of the window, we estimate LOS as one step after
            los = times[los_idx] + datetime.timedelta(seconds=step_seconds)

        max_el = np.max(el[pass_indices])

        pass_points = []
        for i in pass_indices:
            pass_points.append({
                'time': times[i],
                'az': float(az[i]),
                'el': float(el[i]),
                'range_km': float(range_km[i])
            })

        return PassData(aos, los, max_el, pass_points)

    def get_julian_date(self, t):
        return jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond * 1e-6)

class PassData:
    def __init__(self, aos, los, max_el, points):
        self.aos = aos
        self.los = los
        self.max_el = max_el
        self.points = points

    def plot_sky(self):
        """Generates a polar plot of the pass."""
        azimuths = np.radians([p['az'] for p in self.points])
        elevations = [p['el'] for p in self.points]

        # In polar plot, r is 90 - elevation (0 at center)
        r = [90 - el for el in elevations]

        plt.figure(figsize=(6, 6))
        ax = plt.subplot(111, projection='polar')
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.plot(azimuths, r, color='b', linewidth=2)
        ax.set_rmax(90)
        ax.set_rticks([0, 30, 60, 90])  # Less radial ticks
        ax.set_yticklabels(['90', '60', '30', '0']) # Elevation labels
        ax.grid(True)
        ax.set_title(f"Skyplot: {self.aos} to {self.los}")
        plt.savefig("skyplot.png")
        print("Saved skyplot to skyplot.png")
