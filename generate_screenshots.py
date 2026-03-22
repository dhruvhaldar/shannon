from playwright.sync_api import sync_playwright
import time
import subprocess
import requests

SERVER_URL = "http://localhost:8010"

def start_server():
    server_process = subprocess.Popen(
        ["python", "run_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    max_retries = 30
    for _ in range(max_retries):
        try:
            response = requests.get(SERVER_URL)
            if response.status_code == 200:
                return server_process
        except requests.ConnectionError:
            time.sleep(1)

    server_process.terminate()
    raise RuntimeError("Failed to start the server")

def take_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 800})
        page.goto(SERVER_URL)

        # 1. Link Budget Waterfall
        page.select_option("#link-preset", "leo")
        page.click("#link-budget-form button[type='submit']")
        page.locator("#link-result").wait_for(state="visible")
        # Give it a tiny bit of time to ensure fully rendered
        page.wait_for_timeout(500)
        page.locator("#link-budget-panel").screenshot(path="assets/link_budget_waterfall.png")

        # 2. Pass Prediction Skyplot
        page.fill("#tle1", "1 33591U 09005A   20265.56828552  .00000055  00000-0  57632-4 0  9995")
        page.fill("#tle2", "2 33591  99.1989 123.6338 0013952 147.2885 212.9238 14.12351659595519")
        page.fill("#lat", "59.3498")
        page.fill("#lon", "18.0707")
        page.fill("#alt", "10")
        page.click("#pass-form button[type='submit']")
        page.locator("#skyplot svg").wait_for(state="visible")
        page.wait_for_timeout(500)
        page.locator("#pass-predict-panel").screenshot(path="assets/satellite_pass_skyplot.png")

        # 3. IQ Constellation
        page.select_option("#scheme", "16-QAM")
        page.fill("#snr", "15")
        page.click("#iq-form button[type='submit']")
        page.locator("#iq-canvas").wait_for(state="visible")
        page.wait_for_timeout(500)
        page.locator("#iq-panel").screenshot(path="assets/iq_constellation.png")

        browser.close()

if __name__ == "__main__":
    process = start_server()
    try:
        take_screenshots()
        print("Screenshots taken successfully!")
    finally:
        process.terminate()
        process.wait()
