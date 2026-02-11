import math
import numpy as np
from scipy.special import erfc

class Modulation:
    def __init__(self, scheme='BPSK'):
        self.scheme = scheme

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

        noise = np.random.normal(0, noise_std, (num_symbols, 2)).view(np.complex128).flatten()

        if self.scheme == 'BPSK':
            # Points at -1, +1
            bits = np.random.randint(0, 2, num_symbols)
            symbols = 2 * bits - 1 # -1 or 1
            # Ensure complex type
            symbols = symbols.astype(np.complex128)
        elif self.scheme == 'QPSK':
            # Points at (+-1 +- 1j) / sqrt(2)
            ints = np.random.randint(0, 4, num_symbols)
            symbols = np.exp(1j * (np.pi/4 + ints * np.pi/2))
        elif self.scheme == '16-QAM':
            # Grid -3, -1, 1, 3 per axis, normalized
            # Average power of unnormalized 16-QAM (values -3, -1, 1, 3) is:
            # (2*(1^2 + 3^2))/4 = (2*10)/4 = 5 per dimension. Total 10.
            # So divide by sqrt(10).
            real_part = 2 * np.random.randint(0, 4, num_symbols) - 3
            imag_part = 2 * np.random.randint(0, 4, num_symbols) - 3
            symbols = (real_part + 1j * imag_part) / math.sqrt(10)
        else:
             raise ValueError(f"Unknown modulation scheme: {self.scheme}")

        return symbols + noise
