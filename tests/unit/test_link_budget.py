import pytest
from shannon.link_budget import calculate_fspl, LinkBudget

def test_fspl_accuracy():
    """Verifies Free Space Path Loss calculation against standard."""
    # FSPL for 2.4GHz at 100km is approx 140 dB
    loss = calculate_fspl(frequency=2.4e9, distance=100e3)
    assert abs(loss - 140.05) < 0.1

def test_link_margin():
    link = LinkBudget(frequency=2.4e9, distance_km=600)
    link.set_transmitter(power_dbm=30, cable_loss=1, antenna_gain=0) # 1W Tx
    link.add_path_loss(atmosphere_loss=0.5)
    link.set_receiver(antenna_gain=15, noise_temp=150)

    margin = link.calculate_margin(data_rate=9600, required_eb_no=10.0)
    # Expected margin calculation:
    # FSPL ~ 155.6 dB
    # EIRP = 29 dBm
    # Rx Pwr ~ -112.1 dBm
    # N0 ~ -176.8 dBm/Hz
    # C/N0 ~ 64.7 dBHz
    # 10logR ~ 39.8
    # Eb/N0 ~ 24.9 dB
    # Margin ~ 14.9 dB

    assert margin > 14.0
    assert margin < 16.0
