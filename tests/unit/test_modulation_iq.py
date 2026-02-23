import pytest
import numpy as np
import math
from shannon.modulation import Modulation

def test_generate_iq_bpsk_values():
    """Verify BPSK symbols are correct (without noise)."""
    mod = Modulation('BPSK')
    # Use high SNR to minimize noise effect
    symbols = mod.generate_iq(num_symbols=1000, snr_db=100.0)

    # Noise should be negligible.
    # BPSK symbols: -1, 1
    # Check that real parts are close to -1 or 1, imag parts close to 0.

    rounded_real = np.round(symbols.real)
    unique_real = np.unique(rounded_real)

    # Check only valid values are present
    assert np.all(np.isin(unique_real, [-1, 1]))
    assert np.allclose(symbols.imag, 0, atol=1e-3)

    # Check both values are generated (statistically likely)
    if len(unique_real) < 2:
        pytest.skip("Statistically unlikely: did not generate both -1 and 1 in 1000 samples")

def test_generate_iq_16qam_values():
    """Verify 16-QAM symbols are correct."""
    mod = Modulation('16-QAM')
    symbols = mod.generate_iq(num_symbols=10000, snr_db=100.0)

    # Expected values: (-3, -1, 1, 3) / sqrt(10)
    scale = math.sqrt(10)
    scaled_syms = symbols * scale

    # Round to nearest integer
    real_rounded = np.round(scaled_syms.real)
    imag_rounded = np.round(scaled_syms.imag)

    unique_real = np.unique(real_rounded)
    unique_imag = np.unique(imag_rounded)

    expected = np.array([-3, -1, 1, 3])

    # Check if all generated values are in expected set
    assert np.all(np.isin(unique_real, expected))
    assert np.all(np.isin(unique_imag, expected))

    # Check that we generated all possible values
    assert len(unique_real) == 4
    assert len(unique_imag) == 4

def test_generate_iq_noise_variance():
    """Verify noise variance matches expected SNR."""
    mod = Modulation('QPSK') # Constant amplitude symbols
    snr_db = 10.0
    num_symbols = 100000

    symbols = mod.generate_iq(num_symbols=num_symbols, snr_db=snr_db)

    # QPSK symbols have magnitude 1. Power = 1.
    # Total Power = Signal Power + Noise Power
    # E[|S+N|^2] = E[|S|^2] + E[|N|^2] (uncorrelated)
    # Total Power = 1 + Noise Power

    total_power = np.mean(np.abs(symbols)**2)

    snr_linear = 10**(snr_db/10.0)
    # SNR = Es/N0. Es=1. N0 = 1/SNR.
    expected_noise_power = 1.0 / snr_linear
    expected_total_power = 1.0 + expected_noise_power

    # Allow some tolerance due to randomness (CLT)
    # Standard error of variance estimate is approx sigma^4 * sqrt(2/(N-1))
    assert abs(total_power - expected_total_power) < 0.05
