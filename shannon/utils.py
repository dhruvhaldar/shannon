
# Physical Constants
BOLTZMANN = 1.380649e-23  # J/K
SPEED_OF_LIGHT = 299792458  # m/s
EARTH_RADIUS_KM = 6371.0  # km

def db_to_linear(db_value):
    """Converts a value in dB to linear scale."""
    return 10 ** (db_value / 10.0)

def linear_to_db(linear_value):
    """Converts a linear value to dB scale."""
    import math
    if linear_value <= 0:
        return -float('inf')
    return 10 * math.log10(linear_value)
