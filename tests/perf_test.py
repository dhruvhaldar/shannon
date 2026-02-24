from playwright.sync_api import sync_playwright
import time
import sys

def run_perf_test(output_path="tests/constellation_benchmark.png"):
    print(f"Running benchmark...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("http://localhost:8000/")
        except Exception as e:
            print(f"Error navigating to app: {e}")
            sys.exit(1)

        # Generate data
        generate_script = """
        () => {
            const numPoints = 100000;
            const data = [];
            for (let i = 0; i < numPoints; i++) {
                const i_val = (Math.random() * 4) - 2;
                const q_val = (Math.random() * 4) - 2;
                data.push([i_val, q_val]);
            }
            return data;
        }
        """
        data = page.evaluate(generate_script)

        # Define benchmark function
        benchmark_script = """
        (data) => {
            const start = performance.now();
            drawConstellation(data);
            const end = performance.now();
            return end - start;
        }
        """

        # Warmup
        page.evaluate(benchmark_script, data)

        # Benchmark
        duration_ms = page.evaluate(benchmark_script, data)
        print(f"Time to draw 100,000 points: {duration_ms:.2f} ms")

        # Screenshot
        page.screenshot(path=output_path)
        print(f"Screenshot saved to {output_path}")

        browser.close()

if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "tests/constellation_benchmark.png"
    run_perf_test(output)
