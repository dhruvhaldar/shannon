import math
import numpy as np
from scipy.special import erfc

class Modulation:
    # Precompute QPSK constellation points
    QPSK_SYMBOLS = np.exp(1j * (np.pi/4 + np.arange(4) * np.pi/2))

    # Precompute BPSK constellation points: -1, +1
    BPSK_SYMBOLS = np.array([-1, 1], dtype=np.complex128)

    # Precompute 16-QAM constellation points
    # Grid -3, -1, 1, 3 per axis.
    # We generate all combinations of real and imaginary parts.
    # Then normalize by sqrt(10).
    _qam_vals = np.array([-3, -1, 1, 3])
    _qam_real, _qam_imag = np.meshgrid(_qam_vals, _qam_vals)
    QAM16_SYMBOLS = (_qam_real + 1j * _qam_imag).flatten() / math.sqrt(10)

    def __init__(self, scheme='BPSK', seed=None):
        self.scheme = scheme
        self.rng = np.random.default_rng(seed)

    def ber_formula(self, eb_no_db):
        """
        Calculates Bit Error Rate (BER) for a given Eb/N0 (in dB).
        """
        eb_no_linear = 10 ** (eb_no_db / 10.0)

        if self.scheme == 'BPSK' or self.scheme == 'QPSK':
            # BER = 0.5 * erfc(sqrt(Eb/N0))
            return 0.5 * erfc(math.sqrt(eb_no_linear))
        elif self.scheme == '16-QAM':
            # Approximation
            # BER ~= 3/8 * erfc(sqrt(2/5 * Eb/N0)) for Gray coding?
            # Standard formula for M-QAM: P_b ~= (4/log2(M)) * (1 - 1/sqrt(M)) * Q(sqrt(3*log2(M)/(M-1) * Eb/N0))
            # For 16-QAM: M=16. log2(M)=4.
            # P_b ~= (4/4) * (1 - 1/4) * Q(...) = 0.75 * Q(...)
            # Argument inside Q: 3*4/15 * Eb/N0 = 12/15 * Eb/N0 = 0.8 * Eb/N0
            # Q(x) = 0.5 * erfc(x/sqrt(2))
            # So BER ~= 0.75 * 0.5 * erfc(sqrt(0.8 * Eb/N0 / 2)) = 0.375 * erfc(sqrt(0.4 * Eb/N0))
            return 0.375 * erfc(math.sqrt(0.4 * eb_no_linear))
        else:
            raise ValueError(f"Unknown modulation scheme: {self.scheme}")

    def generate_iq(self, num_symbols=1000, snr_db=10.0):
        """
        Generates random IQ points for the modulation scheme with noise.
        """
        snr_linear = 10 ** (snr_db / 10.0)
        # Signal power is usually normalized to 1 per symbol
        # Noise power (N0) -> SNR = Es/N0
        # If Es = 1, N0 = 1/SNR
        # Noise std dev (per dimension I/Q) = sqrt(N0/2) = sqrt(1/(2*SNR))

        noise_std = math.sqrt(1.0 / (2.0 * snr_linear))

        noise = self.rng.normal(0, noise_std, 2 * num_symbols).view(np.complex128)

        if self.scheme == 'BPSK':
            # Points at -1, +1
            bits = self.rng.integers(0, 2, num_symbols)
            symbols = self.BPSK_SYMBOLS[bits]
        elif self.scheme == 'QPSK':
            # Points at (+-1 +- 1j) / sqrt(2)
            ints = self.rng.integers(0, 4, num_symbols)
            symbols = self.QPSK_SYMBOLS[ints]
        elif self.scheme == '16-QAM':
            # Grid -3, -1, 1, 3 per axis, normalized
            ints = self.rng.integers(0, 16, num_symbols)
            symbols = self.QAM16_SYMBOLS[ints]
        else:
             raise ValueError(f"Unknown modulation scheme: {self.scheme}")

        return symbols + noise
