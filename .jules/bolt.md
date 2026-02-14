## 2023-10-27 - Vectorizing SGP4 Propagation
**Learning:** Replacing iterative SGP4 propagation with `sgp4_array` and vectorized numpy math provides significant speedup (~4x for 10 days), but requires careful handling of edge cases like pass truncation at window boundaries to match iterative behavior.
**Action:** When vectorizing time-series simulations, ensure boundary conditions (start/end of window) match the original iterative logic or are explicitly defined.
