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

    def compute_look_angles(self, satellite_eci, time):
        """
        Computes Azimuth and Elevation from the ground station to the satellite.
        satellite_eci: [x, y, z] in km (TEME/ECI frame)
        time: datetime object
        """
        # Convert satellite ECI to ECEF
        # This requires GMST calculation

        gmst = self._calculate_gmst(time)
        sat_ecef = self._eci_to_ecef(satellite_eci, gmst)

        # Vector from station to satellite in ECEF
        rx_vec = sat_ecef - self.location
        range_km = np.linalg.norm(rx_vec)

        # Convert to Topocentric Horizon (SEZ) system
        # We need to rotate from ECEF to SEZ (South-East-Zenith) or ENU (East-North-Up)
        # Let's use ENU

        lat_rad = math.radians(self.lat)
        lon_rad = math.radians(self.lon)

        sin_lat = math.sin(lat_rad)
        cos_lat = math.cos(lat_rad)
        sin_lon = math.sin(lon_rad)
        cos_lon = math.cos(lon_rad)

        dx, dy, dz = rx_vec

        # ENU transformation matrix
        # E = -sin_lon * dx + cos_lon * dy
        # N = -sin_lat * cos_lon * dx - sin_lat * sin_lon * dy + cos_lat * dz
        # U = cos_lat * cos_lon * dx + cos_lat * sin_lon * dy + sin_lat * dz

        e = -sin_lon * dx + cos_lon * dy
        n = -sin_lat * cos_lon * dx - sin_lat * sin_lon * dy + cos_lat * dz
        u = cos_lat * cos_lon * dx + cos_lat * sin_lon * dy + sin_lat * dz

        # Calculate Az/El
        # Azimuth is measured clockwise from North
        az = math.degrees(math.atan2(e, n))
        if az < 0:
            az += 360.0

        el = math.degrees(math.asin(u / range_km))

        return az, el, range_km

    def _calculate_gmst(self, time):
        """Calculates Greenwich Mean Sidereal Time."""
        # JD calculation
        jd, fr = jday(time.year, time.month, time.day, time.hour, time.minute, time.second + time.microsecond * 1e-6)

        # GMST approximation
        t_ut1 = jd + fr - 2451545.0
        gmst = 280.46061837 + 360.98564736629 * t_ut1
        gmst %= 360.0
        return math.radians(gmst)

    def _eci_to_ecef(self, eci, gmst):
        """Rotates ECI vector to ECEF using GMST."""
        x, y, z = eci
        cos_g = math.cos(gmst)
        sin_g = math.sin(gmst)

        x_ecef = x * cos_g + y * sin_g
        y_ecef = -x * sin_g + y * cos_g
        z_ecef = z

        return np.array([x_ecef, y_ecef, z_ecef])
