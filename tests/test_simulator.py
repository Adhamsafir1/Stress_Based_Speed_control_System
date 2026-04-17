"""tests/test_simulator.py — Unit tests for the sensor data acquisition layer."""

import time
import pytest
from sensor.simulator import StressSimulator, SensorReading


class TestSensorReading:
    def test_to_dict_contains_all_keys(self):
        r = SensorReading(timestamp=0.0, heart_rate=75, gsr=2.5, spo2=98)
        keys = r.to_dict().keys()
        assert {"timestamp", "heart_rate", "gsr", "spo2", "stress_score"}.issubset(keys)

    def test_values_are_numeric(self):
        r = SensorReading(timestamp=1.0, heart_rate=80, gsr=3.0, spo2=97)
        d = r.to_dict()
        assert isinstance(d["heart_rate"], float)
        assert isinstance(d["gsr"], float)
        assert isinstance(d["spo2"], float)


class TestStressSimulator:
    def setup_method(self):
        self.sim = StressSimulator(sample_rate=10.0, noise_factor=0.01)

    def test_get_sample_returns_sensor_reading(self):
        r = self.sim.get_sample()
        assert isinstance(r, SensorReading)

    def test_heart_rate_physiologically_valid(self):
        for _ in range(100):
            r = self.sim.get_sample()
            assert 30 <= r.heart_rate <= 220, f"HR out of range: {r.heart_rate}"

    def test_gsr_positive(self):
        for _ in range(100):
            r = self.sim.get_sample()
            assert r.gsr >= 0, f"GSR negative: {r.gsr}"

    def test_spo2_under_100(self):
        for _ in range(100):
            r = self.sim.get_sample()
            assert r.spo2 <= 100.5, f"SpO2 > 100: {r.spo2}"

    def test_stress_score_in_valid_range(self):
        for _ in range(100):
            r = self.sim.get_sample()
            assert 0 <= r.stress_score <= 100, f"Score out of range: {r.stress_score}"

    def test_starts_in_normal_level(self):
        assert self.sim._current_level == "normal"

    def test_callback_receives_readings(self):
        received = []
        self.sim.register_callback(received.append)
        self.sim.start()
        time.sleep(0.5)
        self.sim.stop()
        assert len(received) > 0, "No callbacks received"

    def test_callback_delivers_sensor_readings(self):
        received = []
        self.sim.register_callback(received.append)
        self.sim.start()
        time.sleep(0.3)
        self.sim.stop()
        for r in received:
            assert isinstance(r, SensorReading)
