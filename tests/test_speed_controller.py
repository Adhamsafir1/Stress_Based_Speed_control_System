"""tests/test_speed_controller.py — Unit tests for the speed control layer."""

import time
import pytest
from controller.speed_controller import SpeedController
from controller.mapping import get_speed_recommendation, SPEED_LIMITS
from controller.alerts import AlertManager, Alert


class TestSpeedController:
    def setup_method(self):
        self.ctrl = SpeedController(
            initial_speed=60.0,
            max_speed=100.0,
            min_speed=20.0,
            transition_rate=50.0,  # fast for tests
        )

    def test_initial_speed(self):
        assert self.ctrl.current_speed == 60.0

    def test_set_target_clamps_max(self):
        self.ctrl.set_target(200.0)
        assert self.ctrl.target_speed == 100.0

    def test_set_target_clamps_min(self):
        self.ctrl.set_target(0.0)
        assert self.ctrl.target_speed == 20.0

    def test_set_target_valid(self):
        self.ctrl.set_target(70.0)
        assert self.ctrl.target_speed == 70.0

    def test_speed_transitions_toward_target(self):
        self.ctrl.start()
        self.ctrl.set_target(80.0)
        time.sleep(0.5)
        self.ctrl.stop()
        assert self.ctrl.current_speed > 60.0

    def test_get_status_returns_dict(self):
        status = self.ctrl.get_status()
        assert "current_speed" in status
        assert "target_speed" in status
        assert "at_target" in status


class TestSpeedMapping:
    def test_normal_level_gives_full_speed(self):
        rec = get_speed_recommendation("normal", 15.0)
        assert rec.target_speed == SPEED_LIMITS["normal"]

    def test_critical_level_gives_minimum(self):
        rec = get_speed_recommendation("critical", 90.0)
        assert rec.target_speed == SPEED_LIMITS["critical"]

    def test_recommendation_has_message(self):
        rec = get_speed_recommendation("high", 70.0)
        assert len(rec.message) > 0

    def test_all_levels_have_mapping(self):
        for level in ("normal", "mild", "high", "critical"):
            rec = get_speed_recommendation(level, 50.0)
            assert rec.target_speed > 0


class TestAlertManager:
    def setup_method(self):
        self.mgr = AlertManager(cooldown_seconds=0.0)

    def test_normal_does_not_trigger_alert(self):
        alerts = []
        self.mgr.register_callback(alerts.append)
        self.mgr.process("normal", 15.0, "All good")
        assert len(alerts) == 0

    def test_high_stress_triggers_alert(self):
        alerts = []
        self.mgr.register_callback(alerts.append)
        self.mgr.process("high", 75.0, "High stress!")
        assert len(alerts) == 1

    def test_alert_has_correct_level(self):
        alerts = []
        self.mgr.register_callback(alerts.append)
        self.mgr.process("critical", 90.0, "Critical!")
        assert alerts[0].stress_level == "critical"

    def test_get_history_returns_list(self):
        self.mgr.process("mild", 45.0, "Mild stress")
        history = self.mgr.get_history()
        assert isinstance(history, list)
        assert len(history) >= 1
