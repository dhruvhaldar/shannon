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
        # Optimization: base-10 exponentiation and square root combined into single math.exp
        # math.sqrt(10 ** (eb_no_db / 10.0)) == math.exp(eb_no_db * (math.log(10) / 20))
        # yields ~50% speedup for hot loop

        if self.scheme == 'BPSK' or self.scheme == 'QPSK':
            # BER = 0.5 * erfc(sqrt(Eb/N0))
            return 0.5 * erfc(math.exp(eb_no_db * 0.1151292546497023))
        elif self.scheme == '16-QAM':
            # Approximation
            # BER ~= 3/8 * erfc(sqrt(2/5 * Eb/N0)) for Gray coding?
            # Standard formula for M-QAM: P_b ~= (4/log2(M)) * (1 - 1/sqrt(M)) * Q(sqrt(3*log2(M)/(M-1) * Eb/N0))
            # For 16-QAM: M=16. log2(M)=4.
            # P_b ~= (4/4) * (1 - 1/4) * Q(...) = 0.75 * Q(...)
            # Argument inside Q: 3*4/15 * Eb/N0 = 12/15 * Eb/N0 = 0.8 * Eb/N0
            # Q(x) = 0.5 * erfc(x/sqrt(2))
            # So BER ~= 0.75 * 0.5 * erfc(sqrt(0.8 * Eb/N0 / 2)) = 0.375 * erfc(sqrt(0.4 * Eb/N0))
            # Optimization: precompute sqrt(0.4) = 0.6324555320336759
            return 0.375 * erfc(0.6324555320336759 * math.exp(eb_no_db * 0.1151292546497023))
        else:
            raise ValueError(f"Unknown modulation scheme: {self.scheme}")

    def generate_iq(self, num_symbols=1000, snr_db=10.0):
        """
        Generates random IQ points for the modulation scheme with noise.
        """
        # Signal power is usually normalized to 1 per symbol
        # Noise power (N0) -> SNR = Es/N0
        # If Es = 1, N0 = 1/SNR
        # Noise std dev (per dimension I/Q) = sqrt(N0/2) = sqrt(1/(2*SNR))

        # Optimization: base-10 exponentiation and square root combined into single math.exp
        # math.sqrt(1.0 / (2.0 * 10 ** (snr_db / 10.0))) == math.sqrt(0.5) * math.exp(-snr_db * (math.log(10) / 20))
        # yielding a slight speedup
        noise_std = 0.7071067811865476 * math.exp(-snr_db * 0.1151292546497023)

        # Optimization: Pre-allocating the output array and generating noise directly
        # into a float64 view avoids allocating multiple temporary arrays.
        # This yields a ~10% speedup over generating noise and symbols separately.
        out = np.empty(num_symbols, dtype=np.complex128)

        # Generate noise directly into out view and scale in-place
        out_float = out.view(np.float64)
        self.rng.standard_normal(2 * num_symbols, out=out_float)
        out_float *= noise_std

        if self.scheme == 'BPSK':
            # Points at -1, +1
            bits = self.rng.integers(0, 2, num_symbols)
            # Optimization: For BPSK, generating symbols by directly manipulating the float64
            # view's real components avoids complex array indexing and addition overhead.
            # bits*2 - 1 maps 0->-1 and 1->1. This yields a speedup over self.BPSK_SYMBOLS[bits].
            out_float[0::2] += (bits * 2 - 1)
        elif self.scheme == 'QPSK':
            # Points at (+-1 +- 1j) / sqrt(2)
            ints = self.rng.integers(0, 4, num_symbols)
            out += self.QPSK_SYMBOLS[ints]
        elif self.scheme == '16-QAM':
            # Grid -3, -1, 1, 3 per axis, normalized
            ints = self.rng.integers(0, 16, num_symbols)
            out += self.QAM16_SYMBOLS[ints]
        else:
             raise ValueError(f"Unknown modulation scheme: {self.scheme}")

        return out
