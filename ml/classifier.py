from dataclasses import dataclass

from sensor.simulator import SensorReading


@dataclass
class ClassificationResult:
    stress_score: float
    stress_level: str
    hr_score: float
    gsr_score: float
    spo2_score: float
    confidence: float

    def to_dict(self):
        return {
            "stress_score":  round(self.stress_score, 1),
            "stress_level":  self.stress_level,
            "hr_score":      round(self.hr_score, 1),
            "gsr_score":     round(self.gsr_score, 1),
            "spo2_score":    round(self.spo2_score, 1),
            "confidence":    round(self.confidence, 2),
        }


class RuleBasedClassifier:
    """
    Threshold-based stress classifier using physiological signal rules.

    Each sensor channel contributes a sub-score (0-100).
    A weighted average produces the composite stress score.

    Stress Level   Score Range   Speed Limit
    ─────────────  ───────────   ───────────
    normal          0 – 30        100 km/h
    mild           31 – 60         70 km/h
    high           61 – 80         50 km/h
    critical       81 – 100        30 km/h
    """

    # (threshold_value, score_at_threshold) breakpoints
    HR_THRESHOLDS  = [(60, 0), (80, 10), (95, 30), (110, 55), (130, 75), (155, 100)]
    GSR_THRESHOLDS = [(1, 0),  (3, 15),  (6, 40),  (9,  65),  (13, 85),  (20, 100)]
    SPO2_THRESH    = [(100,0), (98,10),  (96,30),  (94,55),   (92,75),   (90, 100)]

    WEIGHTS = {"hr": 0.40, "gsr": 0.40, "spo2": 0.20}
    LEVEL_CUTOFFS = {"normal": 30, "mild": 60, "high": 80}

    @classmethod
    def classify(cls, reading: SensorReading) -> ClassificationResult:
        hr_s   = cls._interp(reading.heart_rate, cls.HR_THRESHOLDS)
        gsr_s  = cls._interp(reading.gsr,        cls.GSR_THRESHOLDS)
        spo2_s = cls._interp(reading.spo2,        cls.SPO2_THRESH, invert=True)

        score = (
            cls.WEIGHTS["hr"]   * hr_s +
            cls.WEIGHTS["gsr"]  * gsr_s +
            cls.WEIGHTS["spo2"] * spo2_s
        )
        level = cls._level(score)
        boundary = {"normal": 15, "mild": 45, "high": 70, "critical": 90}[level]
        confidence = max(0.5, 1.0 - abs(score - boundary) / 50)

        return ClassificationResult(
            stress_score=score,
            stress_level=level,
            hr_score=hr_s,
            gsr_score=gsr_s,
            spo2_score=spo2_s,
            confidence=min(1.0, confidence),
        )

    @classmethod
    def _interp(cls, value, breakpoints, invert=False):
        if invert:
            # Higher spo2 = lower stress -> reverse lookup direction
            for i in range(len(breakpoints) - 1):
                v0, s0 = breakpoints[i]
                v1, s1 = breakpoints[i + 1]
                if value >= v1:
                    t = (value - v1) / max(v0 - v1, 1e-9)
                    return s1 + t * (s0 - s1)
            return breakpoints[-1][1]

        for i in range(len(breakpoints) - 1):
            v0, s0 = breakpoints[i]
            v1, s1 = breakpoints[i + 1]
            if value <= v1:
                t = (value - v0) / max(v1 - v0, 1e-9)
                return s0 + t * (s1 - s0)
        return breakpoints[-1][1]

    @classmethod
    def _level(cls, score) -> str:
        if score <= cls.LEVEL_CUTOFFS["normal"]:
            return "normal"
        if score <= cls.LEVEL_CUTOFFS["mild"]:
            return "mild"
        if score <= cls.LEVEL_CUTOFFS["high"]:
            return "high"
        return "critical"
