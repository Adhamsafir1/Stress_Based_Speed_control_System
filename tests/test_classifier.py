"""tests/test_classifier.py — Unit tests for the stress classification layer."""

import pytest
from sensor.simulator import SensorReading
from ml.classifier import RuleBasedClassifier, ClassificationResult


def reading(hr, gsr, spo2) -> SensorReading:
    return SensorReading(timestamp=0.0, heart_rate=hr, gsr=gsr, spo2=spo2)


class TestRuleBasedClassifier:
    def test_returns_classification_result(self):
        r = RuleBasedClassifier.classify(reading(75, 2.0, 98))
        assert isinstance(r, ClassificationResult)

    def test_low_hr_gsr_high_spo2_is_normal(self):
        r = RuleBasedClassifier.classify(reading(65, 1.2, 99))
        assert r.stress_level == "normal"
        assert r.stress_score <= 30

    def test_very_high_hr_is_critical(self):
        r = RuleBasedClassifier.classify(reading(155, 18.0, 90))
        assert r.stress_level == "critical"
        assert r.stress_score >= 80

    def test_score_always_non_negative(self):
        readings = [
            reading(60, 0.5, 100),
            reading(100, 6.0, 96),
            reading(140, 14.0, 91),
        ]
        for rd in readings:
            result = RuleBasedClassifier.classify(rd)
            assert result.stress_score >= 0

    def test_score_max_100(self):
        r = RuleBasedClassifier.classify(reading(200, 25.0, 85))
        assert result.stress_score <= 100 if (result := r) else True

    def test_confidence_between_0_and_1(self):
        for hr, gsr, spo2 in [(65, 1.5, 99), (95, 5.0, 96), (130, 12.0, 92)]:
            r = RuleBasedClassifier.classify(reading(hr, gsr, spo2))
            assert 0.0 <= r.confidence <= 1.0

    def test_to_dict_has_required_keys(self):
        d = RuleBasedClassifier.classify(reading(75, 2.0, 98)).to_dict()
        for key in ("stress_score", "stress_level", "hr_score", "gsr_score", "confidence"):
            assert key in d, f"Missing key: {key}"

    def test_level_progression_with_increasing_hr(self):
        levels = []
        for hr in [65, 90, 115, 150]:
            r = RuleBasedClassifier.classify(reading(hr, 3.0, 96))
            levels.append(r.stress_level)
        # Expect monotonically increasing severity
        severity = {"normal": 0, "mild": 1, "high": 2, "critical": 3}
        scores = [severity[l] for l in levels]
        assert scores == sorted(scores), f"Non-monotonic: {levels}"
