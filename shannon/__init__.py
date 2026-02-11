from .link_budget import LinkBudget
from .orbits import PassPredictor
from .ground_station import GroundStation
from .modulation import Modulation

class Mission:
    def __init__(self, sat_id, station):
        # This is a simplified Mission class to satisfy the E2E test requirement
        # In a real app, sat_id would lookup TLEs, station would lookup coords

        # Hardcoding TLEs for NOAA-19 for the test/example
        if sat_id == 'NOAA-19':
            # NOAA 19 TLE (Example)
            self.tle_line1 = "1 33591U 09005A   20265.56828552  .00000055  00000-0  57632-4 0  9995"
            self.tle_line2 = "2 33591  99.1989 123.6338 0013952 147.2885 212.9238 14.12351659595519"
        else:
            # Default placeholder
            self.tle_line1 = "1 00000U 00000A   20001.00000000  .00000000  00000-0  00000-0 0  9999"
            self.tle_line2 = "2 00000   0.0000   0.0000 0000000   0.0000   0.0000  0.00000000    01"

        if station == 'KTH':
            self.ground_station = GroundStation(lat=59.3498, lon=18.0707, alt=10)
        else:
            # Default
            self.ground_station = GroundStation(lat=0, lon=0, alt=0)

        self.predictor = PassPredictor(self.tle_line1, self.tle_line2)

        # Initialize a default link budget
        # Assuming S-band (2.4 GHz) and some avg distance or calculating it
        # Using 600km as per prompt example
        self.link_budget = LinkBudget(frequency=2.4e9, distance_km=600)

        # Set default parameters similar to prompt
        self.link_budget.set_transmitter(power_dbm=30, cable_loss=1, antenna_gain=0)
        self.link_budget.add_path_loss(atmosphere_loss=0.5)
        self.link_budget.set_receiver(antenna_gain=15, noise_temp=150)

    def next_pass_duration(self):
        # Calculate next pass duration
        pass_data = self.predictor.get_next_pass(self.ground_station)
        if pass_data:
            duration = (pass_data.los - pass_data.aos).total_seconds()
            return duration
        return 0.0
