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

## 2026-02-25 - Efficient Complex Array Serialization
**Learning:** Serializing large numpy arrays of complex numbers to JSON-compatible lists using a list comprehension (`[[float(r), float(i)] for r, i in ...]`) is significantly slower than using numpy view manipulation. `arr.view(np.float64).reshape(-1, 2).tolist()` is ~3x faster (30ms vs 90ms for 100k points) as it avoids Python loop overhead.
**Action:** When serializing homogeneous numeric data (especially multidimensional or complex) to standard lists, assume `numpy.tolist()` combined with view/reshape is faster than manual iteration.

## 2026-02-26 - Faster Complex Noise Generation
**Learning:** Generating complex Gaussian noise by creating a 2D array of floats `(N, 2)` and then flattening it is slower than generating a contiguous 1D array of floats `2*N` and viewing it as `complex128`. The latter avoids the overhead of multi-dimensional array creation and memory copying/striding. Coupled with `np.random.default_rng()`, this yielded a ~14% speedup.
**Action:** When generating complex noise, use `rng.normal(..., 2*N).view(np.complex128)` instead of generating separate real/imaginary components or multidimensional arrays.

## 2024-05-27 - Fast Vector Magnitude (Numpy Power vs Multiply)
**Learning:** Using the power operator `**2` on numpy arrays (e.g. `x**2 + y**2 + z**2`) triggers allocations via `np.power`, making it slower than direct multiplication (`x*x + y*y + z*z`). Explicit multiplication in `range_km` calculation avoided the temporary power array allocation overhead and yielded a ~25% speedup for magnitude computation.
**Action:** When computing sums of squares on numpy arrays, use explicit element-wise multiplication (`x*x`) instead of the power operator (`x**2`) to avoid unnecessary memory allocations and improve runtime.

## 2026-03-02 - Logarithmic Identity Optimization
**Learning:** In calculations involving a squared term inside a logarithm, such as `10 * log10(x**2)`, the python math module overhead for power and squaring is surprisingly high. Factoring the exponent out using logarithmic properties to `20 * log10(x)` combined with constant precomputation completely bypasses the exponentiation overhead, yielding a significant (~25%) speedup for repeated link budget calculations.
**Action:** For formulas inside logarithmic scales (like dB), always expand the algebra to pull exponents out as multipliers to bypass expensive `**` operations.

## 2026-03-03 - Fast Numpy Array Modulo Optimization
**Learning:** When applying modulo operations (like `% 360.0`) on large floating-point numpy arrays (e.g. normalizing GMST angles), the native python `%` operator triggers `np.fmod` which carries significant overhead. Using the mathematical equivalent `arr -= 360.0 * np.floor(arr / 360.0)` is significantly faster (~30-50% speedup) because it uses simpler, faster vectorized primitives.
**Action:** For large floating-point numpy arrays, use the `np.floor` subtraction pattern instead of `%` to normalize variables within boundaries.

## 2026-03-04 - Normal vs Standard Normal in Numpy
**Learning:** Generating arrays using `rng.normal(mean, std, size)` is noticeably slower than using `rng.standard_normal(size) * std + mean` in numpy, particularly for large arrays. Multiplying standard_normal (which wraps a faster C implementation natively) saves substantial overhead (~15-20% speedup).
**Action:** For heavy loops or large arrays needing Gaussian noise with a custom standard deviation and mean, use `rng.standard_normal() * std + mean` instead of `rng.normal(mean, std)`.

## 2026-03-05 - In-Place Masking vs np.where
**Learning:** For conditional array updates like normalizing angles (`arr = np.where(arr < 0, arr + 360.0, arr)`), `np.where` allocates a completely new array, creating significant overhead (~0.086s for 100k points). Using in-place boolean masking (`arr[arr < 0] += 360.0`) modifies the array directly without allocating a new one, yielding a massive >15x speedup (~0.005s).
**Action:** When updating elements in a numpy array based on a condition, always use in-place boolean masking instead of `np.where` to avoid memory allocation overhead.

## 2026-03-05 - In-Place Complex Array Pre-allocation Optimization
**Learning:** In NumPy, combining an empty array allocation (`np.empty(N, dtype=np.complex128)`), generating standard normal noise directly into its `float64` view (`rng.standard_normal(2 * N, out=out.view(np.float64))`), and doing in-place scalar multiplication and array addition avoids intermediate array instantiations entirely. When generating symbols with noise, this approach (`out += symbols`) is ~10-11% faster than creating two arrays (`noise`, `symbols`) and adding them together `symbols + noise`.
**Action:** For hot loops that combine randomly generated values (like noise) with lookup table outputs (like symbols), allocate an `np.empty` array, populate it directly using the `out=` parameter of the RNG (using views if needed for complex numbers), and use in-place addition `+=`.

## 2026-03-10 - Math Log vs Log10 Base Conversion
**Learning:** The Python `math.log10(x)` function computes `log(x)/log(10)` internally in C, but using `math.log(x)` directly with a precomputed factor `(10 / math.log(10))` avoids an extra C boundary crossing and relies on a faster native CPU instruction. Factoring logarithmic equations in tight loops (e.g., converting `10 * math.log10(x)` to `4.3429... * math.log(x)`) yields a consistent ~20% speedup. For complex expressions like `20 * math.log10(A * B * constant)`, factoring the constant into a precomputed offset `+ 20 * math.log10(constant)` and using `(20 / math.log(10)) * math.log(A * B)` gave a ~25% speedup.
**Action:** In high-frequency tight loops that use `math.log10()`, substitute it with a precomputed factor multiplied by `math.log()`, and precompute constant offsets to avoid repetitive logarithmic evaluations.

## 2026-03-12 - Fast Base-10 Exponentiation
**Learning:** In Python, `10 ** x` (and especially `10 ** (x / 10.0)`) is surprisingly slow compared to calculating the natural exponential using `math.exp(x * constant)`. Using the mathematical identity $10^x = e^{x \ln(10)}$, we can replace `10 ** (x / 10.0)` with `math.exp(x * 0.2302585092994046)`, yielding a ~35-40% speedup. Furthermore, when computing formulas like $\sqrt{1 / (2 \cdot 10^{x/10})}$, expanding and moving the division and square root into the exponential factor ($\sqrt{0.5} \cdot e^{x \cdot -\ln(10)/20}$) eliminates two expensive math operations, resulting in ~47% speedup.
**Action:** Always replace base-10 exponentiation (`10 ** x` or `math.pow(10, x)`) with `math.exp(x * 2.302585092994046)` in performance-critical code. Attempt to simplify adjacent square roots and divisions directly into the exponential's constant multiplier.

## 2026-03-12 - Fast Degrees/Radians Conversion
**Learning:** In NumPy, calling `np.degrees(arr)` and `np.radians(arr)` on large arrays invokes a `ufunc` that is significantly slower (~40-45% overhead) than explicit scalar multiplication `arr * (180.0 / np.pi)` and `arr * (np.pi / 180.0)`. Explicit multiplication utilizes faster basic array operations and avoids the function dispatch and array allocation overhead of the generic `np.degrees`/`np.radians` wrappers.
**Action:** In performance-critical hot loops or over large Numpy arrays (N > 100k points), always use explicit multiplication by `(180.0 / np.pi)` or `(np.pi / 180.0)` instead of `np.degrees()` and `np.radians()`.

## 2026-03-15 - Fast Base-10 Exponentiation and Square Root combined
**Learning:** Combining base-10 exponentiation (`10 ** x`) and `math.sqrt` into a single `math.exp(x * constant)` operation yields significant speedup (~50%) for hot loops in Python. For formulas like `math.sqrt(10 ** (x / 10.0))`, using `math.exp(x * 0.1151292546497023)` is much faster because it avoids separate exponentiation and square root calls, simplifying directly to the natural exponential with a precomputed factor.
**Action:** When computing `math.sqrt(10 ** (x / y))`, algebraically combine the operations into a single `math.exp(x * constant)` call to minimize math module overhead.

## 2026-03-16 - Precomputing Noise Power Density Constants
**Learning:** In `link_budget.py`, when calculating the Noise Power Density `10 * log10(k * T) + 30`, there are redundant math calls. By applying logarithmic identities, this can be expanded to `(10 / ln(10)) * ln(T) + (10 * log10(k) + 30)`. Factoring out the constants and using `math.log` yields a ~35% speedup without altering functionality or risking `T` being `<= 0`.
**Action:** In calculations involving products within logarithms, expand them to `log(A) + log(B)` so the constant parts can be precomputed, accelerating repetitive code.

## 2026-03-16 - np.empty_like vs np.full_like Allocation
**Learning:** In NumPy, `np.empty_like(arr, dtype=...).fill(np.nan)` is noticeably faster (~37%) and has less memory overhead than `np.full_like(arr, np.nan)`. The `full_like` helper incorporates complex internal setup which can be bypassed using explicit allocation and filling.
**Action:** Use `np.empty_like().fill()` over `np.full_like()` when initializing arrays inside critical performance loops.

## 2026-03-16 - BPSK Symbol Generation via Integer Math
**Learning:** In BPSK symbol generation (`Modulation.generate_iq`), creating integer values directly into the real component of the float view (`out.view(np.float64)[0::2] += (2 * bits - 1)`) is ~10% faster than pulling corresponding `-1` and `1` mapped items from a `np.complex128` constant array like `out += BPSK_SYMBOLS[bits]`. This avoids pulling memory structures inside the hot loop.
**Action:** To populate complex values dynamically and performantly on array variables such as `out`, manipulate the float representations directly instead of copying `complex128` items natively.

## 2024-05-28 - BPSK Symbol Generation Optimization
**Learning:** Generating BPSK symbols (-1, 1) by looking up a precomputed `complex128` array (`self.BPSK_SYMBOLS[bits]`) and adding it to the `complex128` output array is slower than performing simple bit arithmetic (`bits * 2 - 1`) and adding the result directly into the real components of the `float64` view of the output array (`out_float[0::2]`).
**Action:** When mapping binary sequences to strictly real-valued components in complex arrays, use integer math and manipulate the `float64` view directly instead of performing complex array indexing and addition.
