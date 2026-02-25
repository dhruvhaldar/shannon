
import numpy as np
import time

def run_benchmark():
    num_symbols = 100000
    print(f"Generating {num_symbols} complex symbols...")
    # Generate random complex data
    symbols = np.random.rand(num_symbols) + 1j * np.random.rand(num_symbols)

    # Method 1: List comprehension (Current)
    print("Running Method 1: List Comprehension...")
    start_time = time.time()
    iq_data1 = [[float(s.real), float(s.imag)] for s in symbols]
    end_time = time.time()
    t1 = end_time - start_time
    print(f"Time: {t1:.4f} seconds")

    # Method 2: Numpy optimized (Proposed)
    print("Running Method 2: Numpy View + Reshape + Tolist...")
    start_time = time.time()
    iq_data2 = symbols.view(np.float64).reshape(-1, 2).tolist()
    end_time = time.time()
    t2 = end_time - start_time
    print(f"Time: {t2:.4f} seconds")

    # Correctness Check
    print("Verifying correctness...")
    # Note: floating point comparison might be tricky due to float() cast vs direct memory view.
    # float(np.float64) preserves value.
    # Let's check a few samples or use np.allclose if we convert back to array.

    # Convert both to numpy arrays for comparison
    arr1 = np.array(iq_data1)
    arr2 = np.array(iq_data2)

    if np.allclose(arr1, arr2):
        print("✅ Results MATCH!")
    else:
        print("❌ Results DO NOT MATCH!")
        # Print first mismatch
        mismatch = np.where(~np.isclose(arr1, arr2))[0]
        if len(mismatch) > 0:
            idx = mismatch[0]
            print(f"Mismatch at index {idx}: {arr1[idx]} vs {arr2[idx]}")

    speedup = t1 / t2 if t2 > 0 else float('inf')
    print(f"Speedup: {speedup:.2f}x")

    if t2 > t1:
        print("⚠️ Warning: Optimization is slower!")
    else:
        print("🚀 Optimization is faster!")

if __name__ == "__main__":
    run_benchmark()
