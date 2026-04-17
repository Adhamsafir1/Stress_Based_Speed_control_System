import numpy as np
from collections import deque
from typing import Optional

from sensor.simulator import SensorReading


class SensorBuffer:
    """
    Sliding window buffer that accumulates sensor readings and extracts
    an 18-dimensional feature vector for the stress classifier.

    Features (per channel: HR, GSR, SpO2):
        mean, std, min, max, linear_slope, range  ->  6 x 3 = 18 features
    """

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self._hr   = deque(maxlen=window_size)
        self._gsr  = deque(maxlen=window_size)
        self._spo2 = deque(maxlen=window_size)

    @property
    def is_ready(self) -> bool:
        return len(self._hr) == self.window_size

    def push(self, reading: SensorReading):
        self._hr.append(reading.heart_rate)
        self._gsr.append(reading.gsr)
        self._spo2.append(reading.spo2)

    def extract_features(self) -> Optional[np.ndarray]:
        if not self.is_ready:
            return None

        def stats(buf):
            a = np.array(buf, dtype=np.float32)
            x = np.arange(len(a))
            slope = float(np.polyfit(x, a, 1)[0])
            return [a.mean(), a.std(), a.min(), a.max(), slope, a.max() - a.min()]

        feats = stats(self._hr) + stats(self._gsr) + stats(self._spo2)
        return np.array(feats, dtype=np.float32)


class SignalNormalizer:
    """Clips sensor values to physiologically valid ranges."""

    RANGES = {
        "heart_rate": (40.0,  200.0),
        "gsr":        (0.0,    25.0),
        "spo2":       (85.0,  100.0),
    }

    @classmethod
    def clip_outliers(cls, reading: SensorReading) -> SensorReading:
        lo, hi = cls.RANGES["heart_rate"]
        reading.heart_rate = max(lo, min(hi, reading.heart_rate))
        lo, hi = cls.RANGES["gsr"]
        reading.gsr = max(lo, min(hi, reading.gsr))
        lo, hi = cls.RANGES["spo2"]
        reading.spo2 = max(lo, min(hi, reading.spo2))
        return reading
