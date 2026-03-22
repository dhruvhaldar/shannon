import pytest
import subprocess
import time
import requests
import os
from playwright.sync_api import Page, expect

SERVER_URL = "http://localhost:8010"

@pytest.fixture(scope="session", autouse=True)
def start_server():
    # Start the server as a background process
    server_process = subprocess.Popen(
        ["python", "run_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for the server to be ready
    max_retries = 30
    for _ in range(max_retries):
        try:
            response = requests.get(SERVER_URL)
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        server_process.terminate()
        raise RuntimeError("Failed to start the server")

    yield

    # Teardown: stop the server
    server_process.terminate()
    server_process.wait()

def test_link_budget_calculator_manual_entry(page: Page):
    """Test setting up a link budget and calculating the margin manually."""
    page.goto(SERVER_URL)

    # Fill in the form fields
    page.fill("#freq", "2400000000")
    page.fill("#dist", "600")
    page.fill("#tx_pwr", "30")
    page.fill("#tx_loss", "1")
    page.fill("#tx_gain", "0")
    page.fill("#atm_loss", "0.5")
    page.fill("#rx_gain", "15")
    page.fill("#rx_temp", "150")
    page.fill("#rate", "9600")
    page.fill("#req_ebno", "10")

    # Click calculate
    page.click("#link-budget-form button[type='submit']")

    # Wait for result to appear and verify
    result_div = page.locator("#link-result")
    expect(result_div).to_contain_text("Margin:")
    expect(result_div).to_contain_text("FSPL:")
    expect(result_div).to_contain_text("Atmosphere Loss:")

def test_link_budget_calculator_preset(page: Page):
    """Test loading a preset scenario and calculating the margin."""
    page.goto(SERVER_URL)

    # Select LEO preset
    page.select_option("#link-preset", "leo")

    # Verify auto-fill (checking a couple of fields)
    expect(page.locator("#freq")).to_have_value("2200000000")
    expect(page.locator("#dist")).to_have_value("600")

    # Click calculate
    page.click("#link-budget-form button[type='submit']")

    # Wait for result to appear and verify
    result_div = page.locator("#link-result")
    expect(result_div).to_contain_text("Margin:")
    expect(result_div).to_contain_text("FSPL:")

def test_pass_prediction(page: Page):
    """Test predicting the next pass with TLE data."""
    page.goto(SERVER_URL)

    # Fill in TLE and location
    page.fill("#tle1", "1 33591U 09005A   20265.56828552  .00000055  00000-0  57632-4 0  9995")
    page.fill("#tle2", "2 33591  99.1989 123.6338 0013952 147.2885 212.9238 14.12351659595519")
    page.fill("#lat", "59.3498")
    page.fill("#lon", "18.0707")
    page.fill("#alt", "10")

    # Click predict
    page.click("#pass-form button[type='submit']")

    # Wait for result to appear and verify
    skyplot = page.locator("#skyplot")
    expect(skyplot).to_contain_text("AOS:")
    expect(skyplot).to_contain_text("LOS:")
    expect(skyplot).to_contain_text("Max El:")

def test_iq_constellation(page: Page):
    """Test visualizing an IQ Constellation."""
    page.goto(SERVER_URL)

    # Select scheme and SNR
    page.select_option("#scheme", "QPSK")
    page.fill("#snr", "15")

    # Click visualize
    page.click("#iq-form button[type='submit']")

    # Wait for status update
    status = page.locator("#iq-status")
    expect(status).to_contain_text("Constellation updated.")

    # Ensure empty state is hidden and canvas is visible
    expect(page.locator("#iq-empty-state")).to_be_hidden()
    expect(page.locator("#iq-canvas")).to_be_visible()
