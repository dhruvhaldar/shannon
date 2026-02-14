import unittest
import datetime
from shannon.orbits import PassPredictor
from shannon.ground_station import GroundStation

class TestPassPrediction(unittest.TestCase):
    def test_pass_prediction_baseline(self):
        tle_line1 = "1 25544U 98067A   23345.67890123  .00012345  00000-0  12345-3 0  9999"
        tle_line2 = "2 25544  51.6416 123.4567 0001234 123.4567 321.4567 15.54321098123456"

        station = GroundStation(37.7749, -122.4194, 0)
        predictor = PassPredictor(tle_line1, tle_line2)

        # Use a fixed start time for reproducibility
        start_time = datetime.datetime(2023, 12, 12, 12, 0, 0)

        pass_data = predictor.get_next_pass(station, start_time, max_duration_hours=24)

        self.assertIsNotNone(pass_data)
        self.assertEqual(pass_data.aos, datetime.datetime(2023, 12, 12, 12, 5, 30))
        self.assertEqual(pass_data.los, datetime.datetime(2023, 12, 12, 12, 15, 30))
        self.assertAlmostEqual(pass_data.max_el, 18.020339782587794, places=4)
        self.assertEqual(len(pass_data.points), 20)

if __name__ == '__main__':
    unittest.main()
