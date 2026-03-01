import math
import matplotlib.pyplot as plt
from shannon.utils import BOLTZMANN, SPEED_OF_LIGHT, linear_to_db, db_to_linear

# Precompute constant for Free Space Path Loss (FSPL) optimization
# 4 * pi / c
_FSPL_CONSTANT = 4 * math.pi / SPEED_OF_LIGHT

def calculate_fspl(frequency, distance):
    """
    Calculates Free Space Path Loss (FSPL) in dB.
    frequency: Hz
    distance: meters
    """
    if distance <= 0 or frequency <= 0:
        return 0.0

    # Optimization: 10 * log10((4 * pi * d * f / c)^2) is equivalent to 20 * log10(4 * pi * d * f / c)
    # Using the precomputed constant and pulling out the exponent (x2 -> 20*) avoids division and power ops
    # resulting in a ~2x speedup.
    return 20 * math.log10(distance * frequency * _FSPL_CONSTANT)

class LinkBudget:
    def __init__(self, frequency, distance_km):
        self.frequency = frequency
        self.distance = distance_km * 1000  # Convert to meters
        self.tx_power_dbm = 0.0
        self.tx_cable_loss = 0.0
        self.tx_antenna_gain = 0.0
        self.rx_antenna_gain = 0.0
        self.rx_noise_temp = 290.0
        self.atmosphere_loss = 0.0
        self.losses = []
        self.last_required_eb_no = 10.0 # Default

    def set_transmitter(self, power_dbm, cable_loss, antenna_gain):
        self.tx_power_dbm = power_dbm
        self.tx_cable_loss = cable_loss
        self.tx_antenna_gain = antenna_gain

    def add_path_loss(self, atmosphere_loss):
        self.atmosphere_loss = atmosphere_loss

    def set_receiver(self, antenna_gain, noise_temp):
        self.rx_antenna_gain = antenna_gain
        self.rx_noise_temp = noise_temp

    def calculate_margin(self, data_rate, required_eb_no):
        """
        Calculates the link margin.
        data_rate: bps
        required_eb_no: dB
        """
        self.last_required_eb_no = required_eb_no

        # EIRP
        eirp = self.tx_power_dbm - self.tx_cable_loss + self.tx_antenna_gain

        # Path Loss
        fspl = calculate_fspl(self.frequency, self.distance)
        total_path_loss = fspl + self.atmosphere_loss

        # Received Power
        rx_power_dbm = eirp - total_path_loss + self.rx_antenna_gain

        # Noise Power Density (N0) = k * T
        n0_w_hz = BOLTZMANN * self.rx_noise_temp
        n0_dbm_hz = linear_to_db(n0_w_hz) + 30

        # Received Eb/N0
        # C/N0 = Pr / N0
        c_n0 = rx_power_dbm - n0_dbm_hz

        # Eb/N0 = C/N0 - 10*log10(Data Rate)
        if data_rate > 0:
            eb_no = c_n0 - 10 * math.log10(data_rate)
        else:
            eb_no = -float('inf')

        margin = eb_no - required_eb_no

        self.losses = [
            ("Tx Power", self.tx_power_dbm),
            ("Cable Loss", -self.tx_cable_loss),
            ("Tx Antenna Gain", self.tx_antenna_gain),
            ("FSPL", -fspl),
            ("Atmosphere Loss", -self.atmosphere_loss),
            ("Rx Antenna Gain", self.rx_antenna_gain)
        ]

        return margin

    def plot_waterfall(self):
        """Generates a waterfall chart of the link budget."""
        if not self.losses:
            print("Run calculate_margin() first.")
            return

        labels = [x[0] for x in self.losses]
        values = [x[1] for x in self.losses]

        cumulative = [values[0]]
        for v in values[1:]:
            cumulative.append(cumulative[-1] + v)

        plt.figure(figsize=(10, 6))
        plt.plot(labels, cumulative, marker='o', linestyle='-')
        plt.title(f"Link Budget Waterfall (Freq: {self.frequency/1e9:.2f} GHz)")
        plt.ylabel("Signal Level (dBm)")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("link_budget_waterfall.png")
        print("Saved waterfall chart to link_budget_waterfall.png")

    def max_data_rate(self, margin_db=3.0, required_eb_no=None):
        if required_eb_no is None:
            required_eb_no = self.last_required_eb_no

        # EIRP
        eirp = self.tx_power_dbm - self.tx_cable_loss + self.tx_antenna_gain

        # Path Loss
        fspl = calculate_fspl(self.frequency, self.distance)
        total_path_loss = fspl + self.atmosphere_loss

        # Received Power
        rx_power_dbm = eirp - total_path_loss + self.rx_antenna_gain

        # Noise Power Density (N0) = k * T
        n0_w_hz = BOLTZMANN * self.rx_noise_temp
        n0_dbm_hz = linear_to_db(n0_w_hz) + 30

        # C/N0
        c_n0 = rx_power_dbm - n0_dbm_hz

        # Actual Eb/N0 needed = Required + Margin
        target_eb_no = required_eb_no + margin_db

        # 10*log10(R) = C/N0 - target_eb_no
        log10_r = (c_n0 - target_eb_no) / 10.0
        return 10 ** log10_r
