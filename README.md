# Shannon

Shannon is a browser-based mission operations suite designed for EF2264 Operation of Space Systems. It combines orbital mechanics with strict RF engineering to simulate the full "Space-to-Ground" communication chain.

Named after Claude Shannon, the father of information theory, this tool allows students to validate link designs, predict satellite passes, and visualize modulation schemes in real-time.

## 📚 Syllabus Mapping (EF2264)

This project strictly adheres to the course learning outcomes:

| Module | Syllabus Topic | Implemented Features |
| :--- | :--- | :--- |
| **Comms Physics** | Physical principles for comms | Friis Transmission Equation, Free Space Path Loss (FSPL), Atmospheric Attenuation. |
| **Link Design** | Use a link budget | Complete Link Budget Calculator (EIRP, G/T, $E_b/N_0$, System Margin). |
| **Orbits** | Practical calculation of orbits | SGP4 propagator for TLEs to determine Acquisition of Signal (AOS) / Loss of Signal (LOS). |
| **Ground Segment** | Structure of ground station | Antenna Pointing calculations (Azimuth/Elevation) and Doppler Shift correction. |
| **Signal Theory** | Modulation and encoding | Digital Modulation simulation (BPSK/QPSK/16-QAM) and Bit Error Rate (BER) estimation. |

## 🚀 Deployment (Vercel)

Shannon is designed to run as a serverless API with a static frontend.

1. Fork this repository.
2. Deploy to Vercel (the `api/` folder is automatically detected).
3. Access your Mission Control at `https://your-shannon.vercel.app`.

## 📊 Artifacts & Operations Analysis

### 1. The Link Budget "Waterfall"

Visualizes the signal power gains and losses from the spacecraft transmitter to the ground receiver.

**Code:**
```python
from shannon.link_budget import LinkBudget

# Design a Low Earth Orbit (LEO) Downlink at 2.4 GHz
link = LinkBudget(frequency=2.4e9, distance_km=600)

# Add Components
link.set_transmitter(power_dbm=30, cable_loss=1, antenna_gain=0) # 1W Tx
link.add_path_loss(atmosphere_loss=0.5)
link.set_receiver(antenna_gain=15, noise_temp=150) # High gain ground yagi

link.calculate_margin(data_rate=9600, required_eb_no=10.0)
link.plot_waterfall()
```

**Artifact Output:**
*Figure 1: Link Budget Waterfall. The chart tracks the signal power (dBm) through the chain. The Free Space Path Loss (FSPL) causes the massive drop, which must be recovered by the Ground Station Antenna Gain ($G_{rx}$) to stay above the Receiver Sensitivity floor.*

### 2. Satellite Pass Prediction (Skyplot)

Predicts the path of a satellite across the local sky for antenna tracking.

**Code:**
```python
from shannon.orbits import PassPredictor
from shannon.ground_station import GroundStation

# Define KTH Ground Station (Stockholm)
kth_station = GroundStation(lat=59.3498, lon=18.0707, alt=10)

# Load TLE for NOAA-19
predictor = PassPredictor(tle_line1="...", tle_line2="...")
pass_data = predictor.get_next_pass(kth_station)

pass_data.plot_sky()
```

**Artifact Output:**
*Figure 2: Ground Track Polar Plot. The center represents the zenith ($90^\circ$ elevation). The curve shows the satellite's trajectory from AOS (Acquisition of Signal) to LOS (Loss of Signal). The red zone indicates the "Keyhole" (high elevation tracking difficulty) or horizon mask.*

### 3. Doppler Shift Simulation

Calculates the frequency shift $\Delta f$ caused by the relative velocity of the spacecraft.

**Artifact Output:**
*Figure 3: The "S-Curve". As the satellite approaches, the frequency is shifted higher (Blue shift). At the Time of Closest Approach (TCA), the shift crosses zero. As it recedes, the frequency shifts lower (Red shift). Ground stations must actively track this changing frequency.*

## 🧪 Testing Strategy

### Unit Tests (RF Engineering)
Located in `tests/unit/`.

**Example:** `tests/unit/test_link_budget.py`
```python
def test_fspl_accuracy():
    """Verifies Free Space Path Loss calculation against standard."""
    from shannon.link_budget import calculate_fspl
    # FSPL for 2.4GHz at 100km is approx 140 dB
    loss = calculate_fspl(frequency=2.4e9, distance=100e3)
    assert abs(loss - 140.05) < 0.1
```

### E2E Tests (Mission Scenario)
Located in `tests/e2e/`.

**Example:** `tests/e2e/test_downlink_feasibility.py`
```python
def test_image_downlink_margin():
    """
    E2E Test: Can we download a 1MB image during a 10-minute pass?
    Requires: Link Margin > 3dB AND Data Rate sufficient.
    """
    mission = Mission(sat_id='NOAA-19', station='KTH')
    pass_duration = mission.next_pass_duration() # e.g., 600s

    link = mission.link_budget
    max_rate = link.max_data_rate(margin_db=3.0)

    total_data = max_rate * pass_duration
    assert total_data > 8e6 # 8 Megabits (1MB)
```

## ⚖️ License

MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files... [Standard MIT Text]
