# Bolt's Journal

## 2024-05-23 - Orbital Pass Prediction Bottleneck
**Learning:** `PassPredictor.get_next_pass` computed SGP4 propagation and look angles for the *entire* requested duration (e.g., 30 days) before filtering for visibility. For sparse events like LEO passes, this wasted >95% of computation time if the pass occurred early.
**Action:** Implemented a chunked search strategy (24h chunks). For future search problems over time series, always consider lazy evaluation or chunking instead of monolithic computation.

## 2024-05-24 - Vectorized Look Angle Computation
**Learning:** In tight loops like look angle calculation (N > 100k points), numpy overhead for `np.stack` and `np.linalg.norm` on small dimensions (3D) is significant. Explicit component-wise operations (x, y, z arrays) avoided intermediate allocations and reduced runtime by ~70% (3.4x speedup).
**Action:** For performance-critical vector operations on fixed small dimensions, prefer component-wise math over generalized numpy functions that allocate intermediate arrays.

## 2024-05-25 - Early Rejection in Look Angles
**Learning:** Calculating `arctan2` and `arcsin` for every point in a satellite pass search is wasteful when >90% of points are below the horizon. Computing just the vertical component `u` (linear dot product) allows early rejection of invisible points, saving expensive trig calls.
**Action:** When filtering geometric data, always check if a cheaper linear condition (like a single component check) can be computed before expensive trigonometric functions.

## 2024-05-26 - Optimized QPSK Symbol Generation
**Learning:** `np.exp` is significantly slower (approx. 30%) than array indexing for small discrete sets (like QPSK constellation). Generating 1M symbols using `np.exp` took ~0.147s, while using a precomputed lookup table took ~0.104s.
**Action:** Always precompute complex constellation points into a lookup table for modulation schemes with small alphabets instead of calculating them on the fly.

## 2026-02-22 - Direct Vertical Component Calculation
**Learning:** For satellite visibility checks, converting ECI to ECEF for every point is wasteful if the point is invisible. The vertical component `u` can be computed directly from ECI coordinates using precomputed rotation components, avoiding full ECEF conversion and reducing intermediate array allocations by ~60% for the invisible path.
**Action:** When transforming coordinates solely to check a threshold (e.g., visibility), derive a direct formula for the check variable in the source frame if possible, rather than transforming the entire state vector.

## 2025-02-23 - Modulation Symbol Generation
**Learning:** Generating modulation symbols by random indexing into a precomputed complex lookup table is ~3.4x faster for 16-QAM than generating real/imaginary components separately and performing arithmetic/normalization on every call.
**Action:** When simulating discrete random variables that map to complex values (like modulation symbols), always prefer `LUT[random_indices]` over arithmetic generation.

## 2026-02-24 - Canvas Scatter Plot Optimization
**Learning:** Batching thousands of `ctx.arc()` calls into a single path was surprisingly SLOWER (~12ms vs 7ms for 20k points) in headless Chrome, likely due to the complexity of rasterizing a path with thousands of subpaths.
**Action:** For high-density scatter plots, replace `ctx.arc()` with `ctx.fillRect()` (drawing small squares). This avoided path construction entirely and yielded a ~2x speedup (96ms vs 194ms for 100k points).
