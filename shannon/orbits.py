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
        Uses a chunked search approach to optimize for long durations.
        """
        if start_time is None:
            start_time = datetime.datetime.utcnow()

        step_seconds = 30

        # Search in 24-hour chunks to avoid computing excessive data
        chunk_size_hours = 24.0
        current_search_time = start_time
        remaining_hours = max_duration_hours

        while remaining_hours > 0:
            this_chunk_hours = min(remaining_hours, chunk_size_hours)

            # Compute pass for this chunk
            pass_data = self._compute_pass_in_window(
                ground_station, current_search_time, this_chunk_hours, step_seconds
            )

            if pass_data:
                # We found a pass!
                # Check if it was truncated by the chunk boundary.
                # If LOS is exactly at the end of our window (within a step), it might be truncated.
                window_end = current_search_time + datetime.timedelta(
                    hours=this_chunk_hours
                )

                # If LOS is very close to window end (e.g. within 2 steps), re-compute to be safe.
                # Using 2 steps (60s) tolerance.
                if pass_data.los >= window_end - datetime.timedelta(
                    seconds=step_seconds * 2
                ):
                    # Truncated or potentially truncated.
                    # Re-compute starting from AOS with enough duration to capture the full pass.
                    # A safe duration for LEO/MEO is 2 hours. For GEO it might be longer, but we respect max_duration.
                    # If the user asked for max_duration, we should ideally search up to that.

                    # Calculate remaining time from AOS
                    time_since_start = (
                        pass_data.aos - start_time
                    ).total_seconds() / 3600.0
                    remaining_from_aos = max_duration_hours - time_since_start

                    # For performance, don't compute more than needed.
                    # If it's LEO, 2 hours is plenty. If it's GEO, we might want more.
                    # But to keep it consistent with "get_next_pass" behavior which returns ONE pass:
                    # If it's a very long pass (GEO), we return up to max_duration.

                    extended_duration = min(
                        remaining_from_aos, 24.0
                    )  # Cap at 24h to avoid huge arrays if it's GEO

                    return self._compute_pass_in_window(
                        ground_station, pass_data.aos, extended_duration, step_seconds
                    )

                return pass_data

            # Advance to next chunk
            current_search_time += datetime.timedelta(hours=this_chunk_hours)
            remaining_hours -= this_chunk_hours

        return None

    def _compute_pass_in_window(
        self, ground_station, start_time, duration_hours, step_seconds
    ):
        duration_seconds = int(duration_hours * 3600)
        num_steps = duration_seconds // step_seconds

        if num_steps <= 0:
            return None

        # Calculate start JD
        jd_start, fr_start = jday(
            start_time.year,
            start_time.month,
            start_time.day,
            start_time.hour,
            start_time.minute,
            start_time.second + start_time.microsecond * 1e-6,
        )

        # Create vectorized time arrays
        # fr (fraction of day) increases by step_seconds / 86400.0 per step
        fr_arr = fr_start + np.arange(num_steps) * (step_seconds / 86400.0)
        jd_arr = np.full(num_steps, jd_start)

        # Vectorized SGP4 propagation
        e, r, v = self.satellite.sgp4_array(jd_arr, fr_arr)

        # Handle errors (e != 0)
        valid_sgp4 = e == 0

        # Vectorized look angles computation
        # Pass all points, filter later
        # We pass time=None because we are providing jd/fr, so GMST calculation doesn't need time object
        az, el, range_km = ground_station.compute_look_angles(
            r, None, jd=jd_arr, fr=fr_arr
        )

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
            pass_indices = valid_indices[: end_idx_in_valid + 1]

        # Extract pass data
        aos_idx = pass_indices[0]
        los_idx = pass_indices[-1]

        aos = start_time + datetime.timedelta(seconds=step_seconds * int(aos_idx))

        # Match iterative behavior: LOS is the time step *after* the last visible point
        los = start_time + datetime.timedelta(seconds=step_seconds * int(los_idx + 1))

        max_el = np.max(el[pass_indices])

        pass_points = []
        for i in pass_indices:
            t = start_time + datetime.timedelta(seconds=step_seconds * int(i))
            pass_points.append(
                {
                    "time": t,
                    "az": float(az[i]),
                    "el": float(el[i]),
                    "range_km": float(range_km[i]),
                }
            )

        return PassData(aos, los, max_el, pass_points)

    def get_julian_date(self, t):
        return jday(
            t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond * 1e-6
        )


class PassData:
    def __init__(self, aos, los, max_el, points):
        self.aos = aos
        self.los = los
        self.max_el = max_el
        self.points = points

    def plot_sky(self):
        """Generates a polar plot of the pass."""
        azimuths = np.radians([p["az"] for p in self.points])
        elevations = [p["el"] for p in self.points]

        # In polar plot, r is 90 - elevation (0 at center)
        r = [90 - el for el in elevations]

        plt.figure(figsize=(6, 6))
        ax = plt.subplot(111, projection="polar")
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.plot(azimuths, r, color="b", linewidth=2)
        ax.set_rmax(90)
        ax.set_rticks([0, 30, 60, 90])  # Less radial ticks
        ax.set_yticklabels(["90", "60", "30", "0"])  # Elevation labels
        ax.grid(True)
        ax.set_title(f"Skyplot: {self.aos} to {self.los}")
        plt.savefig("skyplot.png")
        print("Saved skyplot to skyplot.png")
