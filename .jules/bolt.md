# Bolt's Journal

## 2024-05-23 - Orbital Pass Prediction Bottleneck
**Learning:** `PassPredictor.get_next_pass` computed SGP4 propagation and look angles for the *entire* requested duration (e.g., 30 days) before filtering for visibility. For sparse events like LEO passes, this wasted >95% of computation time if the pass occurred early.
**Action:** Implemented a chunked search strategy (24h chunks). For future search problems over time series, always consider lazy evaluation or chunking instead of monolithic computation.
