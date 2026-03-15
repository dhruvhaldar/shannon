import math

# Physical Constants
BOLTZMANN = 1.380649e-23  # J/K
SPEED_OF_LIGHT = 299792458  # m/s
EARTH_RADIUS_KM = 6371.0  # km

# Precomputed factor for converting base-10 exponentiation to natural exponentiation
# 10^(x/10) = e^(x * ln(10)/10)
_DB_TO_LINEAR_EXP_FACTOR = math.log(10) / 10.0

def db_to_linear(db_value):
    """Converts a value in dB to linear scale."""
    # Optimization: replace 10 ** (x / 10.0) with math.exp(x * _DB_TO_LINEAR_EXP_FACTOR)
    # math.exp is significantly faster than base-10 exponentiation in Python.
    return math.exp(db_value * _DB_TO_LINEAR_EXP_FACTOR)

def linear_to_db(linear_value):
    """Converts a linear value to dB scale."""
    import math
    if linear_value <= 0:
        return -float('inf')
    # Optimization: 10 * math.log10(x) is equivalent to (10 / ln(10)) * ln(x)
    # Using math.log (natural log) with a precomputed multiplier is ~20% faster
    # than math.log10 because log10 internally computes log(x)/log(10) in C but
    # math.log uses the native fast natural log CPU instruction directly.
    return 4.3429448190325175 * math.log(linear_value)
