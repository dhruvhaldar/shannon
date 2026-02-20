import math
import datetime
import numpy as np
from shannon.utils import EARTH_RADIUS_KM
from sgp4.api import jday

class GroundStation:
    def __init__(self, lat, lon, alt):
        self.lat = lat  # Degrees
        self.lon = lon  # Degrees
        self.alt = alt  # Meters

        self.location = self._geodetic_to_ecef(lat, lon, alt)
        self._compute_enu_rotation_matrix()

    def _compute_enu_rotation_matrix(self):
        """Precomputes the ECEF to ENU rotation matrix."""
        lat_rad = math.radians(self.lat)
        lon_rad = math.radians(self.lon)

        sin_lat = math.sin(lat_rad)
        cos_lat = math.cos(lat_rad)
        sin_lon = math.sin(lon_rad)
        cos_lon = math.cos(lon_rad)

        # R matrix (ECEF to ENU)
        # Row 0: [-sin_lon, cos_lon, 0]
        # Row 1: [-sin_lat*cos_lon, -sin_lat*sin_lon, cos_lat]
        # Row 2: [cos_lat*cos_lon, cos_lat*sin_lon, sin_lat]
        self.R = np.array([
            [-sin_lon, cos_lon, 0],
            [-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat],
            [cos_lat * cos_lon, cos_lat * sin_lon, sin_lat]
        ])

    def _geodetic_to_ecef(self, lat, lon, alt):
        # WGS84 ellipsoid constants
        a = 6378.137  # km
        f = 1.0 / 298.257223563
        e2 = 2*f - f*f

        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)

        x = (N + alt/1000.0) * math.cos(lat_rad) * math.cos(lon_rad)
        y = (N + alt/1000.0) * math.cos(lat_rad) * math.sin(lon_rad)
        z = (N * (1 - e2) + alt/1000.0) * math.sin(lat_rad)

        return np.array([x, y, z]) # km

    def compute_look_angles(self, satellite_eci, time, jd=None, fr=None, mask_invisible=False):
        """
        Computes Azimuth and Elevation from the ground station to the satellite.
        satellite_eci: [x, y, z] in km (TEME/ECI frame)
        time: datetime object or list/array of datetime objects
        jd, fr: Optional pre-calculated Julian Date components (to avoid re-calculation)
        mask_invisible: If True, returns NaN for points where satellite is below horizon (optimization).
        """
        # Ensure input is numpy array if list
        if isinstance(satellite_eci, list):
            satellite_eci = np.array(satellite_eci)

        # Convert satellite ECI to ECEF
        # This requires GMST calculation

        gmst = self._calculate_gmst(time, jd=jd, fr=fr)
        sat_ecef_x, sat_ecef_y, sat_ecef_z = self._eci_to_ecef(satellite_eci, gmst)

        # Vector from station to satellite in ECEF
        # Avoid allocating intermediate (N, 3) array
        rx_x = sat_ecef_x - self.location[0]
        rx_y = sat_ecef_y - self.location[1]
        rx_z = sat_ecef_z - self.location[2]

        # Calculate 'Up' component first to check visibility (optimization)
        u = rx_x * self.R[2, 0] + rx_y * self.R[2, 1] + rx_z * self.R[2, 2]

        if mask_invisible and isinstance(u, np.ndarray):
            # Mask where u > 0 (visible)
            visible = u > 0

            # If nothing is visible, return NaNs early
            if not np.any(visible):
                nan_arr = np.full_like(u, np.nan)
                return nan_arr, nan_arr, nan_arr

            # Initialize results with NaNs
            az = np.full_like(u, np.nan)
            el = np.full_like(u, np.nan)
            range_km = np.full_like(u, np.nan)

            # Filter inputs for visible points
            rx_x_vis = rx_x[visible]
            rx_y_vis = rx_y[visible]
            rx_z_vis = rx_z[visible]
            u_vis = u[visible]

            # Calculate range only for visible
            range_km_vis = np.sqrt(rx_x_vis * rx_x_vis + rx_y_vis * rx_y_vis + rx_z_vis * rx_z_vis)

            # Calculate E/N components only for visible
            e_vis = rx_x_vis * self.R[0, 0] + rx_y_vis * self.R[0, 1] + rx_z_vis * self.R[0, 2]
            n_vis = rx_x_vis * self.R[1, 0] + rx_y_vis * self.R[1, 1] + rx_z_vis * self.R[1, 2]

            # Calculate Az/El for visible
            az_vis = np.degrees(np.arctan2(e_vis, n_vis))
            az_vis = np.where(az_vis < 0, az_vis + 360.0, az_vis)
            el_vis = np.degrees(np.arcsin(u_vis / range_km_vis))

            # Assign back to full arrays
            az[visible] = az_vis
            el[visible] = el_vis
            range_km[visible] = range_km_vis

            return az, el, range_km

        # Standard path (full computation)
        # Calculate range
        range_km = np.sqrt(rx_x * rx_x + rx_y * rx_y + rx_z * rx_z)

        # Convert to Topocentric Horizon (SEZ) system
        # We need to rotate from ECEF to SEZ (South-East-Zenith) or ENU (East-North-Up)
        # Let's use ENU

        # Optimization: Use precomputed rotation matrix and component-wise math
        # Avoid matrix multiplication and allocation of intermediate array
        # self.R is 3x3 array
        e = rx_x * self.R[0, 0] + rx_y * self.R[0, 1] + rx_z * self.R[0, 2]
        n = rx_x * self.R[1, 0] + rx_y * self.R[1, 1] + rx_z * self.R[1, 2]
        # u is already calculated above

        # Calculate Az/El
        # Azimuth is measured clockwise from North
        az = np.degrees(np.arctan2(e, n))

        # Handle negative azimuths
        # np.where works for arrays, standard if/else for scalars
        if np.ndim(az) == 0:
            if az < 0:
                az += 360.0
        else:
            az = np.where(az < 0, az + 360.0, az)

        el = np.degrees(np.arcsin(u / range_km))

        return az, el, range_km

    def _calculate_gmst(self, time, jd=None, fr=None):
        """Calculates Greenwich Mean Sidereal Time."""
        if jd is None or fr is None:
            if isinstance(time, (list, np.ndarray)):
                # Vectorized path
                # Assume array of datetime objects
                # We need to extract components efficiently
                # List comprehension is fastest way to unpack datetime objects in python
                # unless we convert to pandas datetime index (heavy dependency)

                ts = np.array(time) if isinstance(time, list) else time

                years = np.array([t.year for t in ts])
                months = np.array([t.month for t in ts])
                days = np.array([t.day for t in ts])
                hours = np.array([t.hour for t in ts])
                minutes = np.array([t.minute for t in ts])
                seconds = np.array([t.second + t.microsecond * 1e-6 for t in ts])

                jd, fr = jday(years, months, days, hours, minutes, seconds)
            else:
                # Scalar path
                jd, fr = jday(time.year, time.month, time.day, time.hour, time.minute, time.second + time.microsecond * 1e-6)

        # GMST approximation
        t_ut1 = jd + fr - 2451545.0
        gmst = 280.46061837 + 360.98564736629 * t_ut1
        gmst %= 360.0
        return np.radians(gmst)

    def _eci_to_ecef(self, eci, gmst):
        """Rotates ECI vector to ECEF using GMST."""
        if eci.ndim == 1:
            x, y, z = eci
        else:
            x, y, z = eci[:, 0], eci[:, 1], eci[:, 2]

        cos_g = np.cos(gmst)
        sin_g = np.sin(gmst)

        x_ecef = x * cos_g + y * sin_g
        y_ecef = -x * sin_g + y * cos_g
        z_ecef = z

        return x_ecef, y_ecef, z_ecef
