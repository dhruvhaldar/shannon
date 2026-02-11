import pytest
from shannon.modulation import Modulation

def test_ber_bpsk():
    mod = Modulation('BPSK')
    # At Eb/N0 = 0 dB -> linear 1.
    # BER = 0.5 * erfc(1) = 0.5 * 0.157299 = 0.0786
    ber = mod.ber_formula(0.0)
    assert abs(ber - 0.0786) < 0.001

def test_ber_qpsk():
    # QPSK has same BER vs Eb/N0 as BPSK
    mod = Modulation('QPSK')
    ber = mod.ber_formula(0.0)
    assert abs(ber - 0.0786) < 0.001
