# Bolt's Journal

## 2024-05-23 - Orbital Pass Prediction Bottleneck
**Learning:** `PassPredictor.get_next_pass` computed SGP4 propagation and look angles for the *entire* requested duration (e.g., 30 days) before filtering for visibility. For sparse events like LEO passes, this wasted >95% of computation time if the pass occurred early.
**Action:** Implemented a chunked search strategy (24h chunks). For future search problems over time series, always consider lazy evaluation or chunking instead of monolithic computation.

## 2024-05-24 - Vectorized Look Angle Computation
**Learning:** In tight loops like look angle calculation (N > 100k points), numpy overhead for `np.stack` and `np.linalg.norm` on small dimensions (3D) is significant. Explicit component-wise operations (x, y, z arrays) avoided intermediate allocations and reduced runtime by ~70% (3.4x speedup).
**Action:** For performance-critical vector operations on fixed small dimensions, prefer component-wise math over generalized numpy functions that allocate intermediate arrays.
