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

        # Simplified pass prediction (brute force for now, can be optimized)
        # Check every 30 seconds for performance
        step = datetime.timedelta(seconds=30)
        current_time = start_time
        end_time = start_time + datetime.timedelta(hours=max_duration_hours)

        aos = None
        los = None
        max_el = 0.0
        pass_points = []

        # First, fast forward to find AOS
        # This is a naive implementation. SGP4 propagation is fast enough for 24h usually.

        while current_time < end_time:
            # We need to compute position
            jd, fr = self.get_julian_date(current_time)
            e, r, v = self.satellite.sgp4(jd, fr)

            if e != 0:
                # Error in propagation
                current_time += step
                continue

            # Convert ECI to Az/El relative to ground station
            az, el, range_km = ground_station.compute_look_angles(r, current_time)

            if el > 0: # Above horizon
                if aos is None:
                    aos = current_time
                    # Backtrack slightly to find exact AOS?
                    # For this prototype, the step granularity is enough.

                max_el = max(max_el, el)
                pass_points.append({
                    'time': current_time,
                    'az': az,
                    'el': el,
                    'range_km': range_km
                })
            else:
                if aos is not None:
                    los = current_time
                    break # Pass ended

            current_time += step

        if aos and los:
            return PassData(aos, los, max_el, pass_points)
        return None

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
