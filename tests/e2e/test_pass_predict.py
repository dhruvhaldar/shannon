import pytest
from shannon import Mission

def test_image_downlink_margin():
    """
    E2E Test: Can we download a 1MB image during a 10-minute pass?
    Requires: Link Margin > 3dB AND Data Rate sufficient.
    """
    mission = Mission(sat_id='NOAA-19', station='KTH')
    pass_duration = mission.next_pass_duration()

    # If pass_duration is 0 (no pass found in next 24h), let's force it to 600s
    # for the sake of testing link budget part.
    # In a real test we would freeze time to a known pass.
    if pass_duration == 0:
        pass_duration = 600.0

    link = mission.link_budget

    max_rate = link.max_data_rate(margin_db=3.0, required_eb_no=10.0)

    total_data = max_rate * pass_duration

    # 1MB = 8 Megabits = 8e6 bits
    assert total_data > 8e6
