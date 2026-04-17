import time
import math
import random
import threading
from dataclasses import dataclass
from typing import Optional


@dataclass
class SensorReading:
    timestamp: float
    heart_rate: float
    gsr: float
    spo2: float
    stress_score: Optional[float] = None

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "heart_rate": round(self.heart_rate, 2),
            "gsr": round(self.gsr, 4),
            "spo2": round(self.spo2, 2),
            "stress_score": self.stress_score,
        }


class StressSimulator:
    """
    Simulates realistic physiological sensor data with stress episodes.

    Stress episodes cycle: Normal -> Mild -> High -> Critical -> High -> Mild -> Normal
    Each channel (HR, GSR, SpO2) has noise and low-frequency oscillation for realism.
    """

    STRESS_PROFILES = {
        "normal":   {"hr": (65, 80),   "gsr": (1.0,  2.5),  "spo2": (97, 100)},
        "mild":     {"hr": (80, 100),  "gsr": (3.0,  6.0),  "spo2": (95,  98)},
        "high":     {"hr": (100, 130), "gsr": (7.0, 12.0),  "spo2": (93,  96)},
        "critical": {"hr": (130, 160), "gsr": (13.0, 20.0), "spo2": (90,  94)},
    }

    STRESS_SCORES = {
        "normal":   (5,  30),
        "mild":     (35, 60),
        "high":     (62, 80),
        "critical": (82, 100),
    }

    EPISODE_DURATIONS = {
        "normal":   30,
        "mild":     20,
        "high":     15,
        "critical": 10,
    }

    SEQUENCE = ["normal", "mild", "high", "critical", "high", "mild", "normal"]

    def __init__(self, sample_rate: float = 10.0, noise_factor: float = 0.05):
        self.sample_rate = sample_rate
        self.noise_factor = noise_factor
        self._interval = 1.0 / sample_rate
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks = []
        self._seq_idx = 0
        self._episode_start = time.time()
        self._current_level = "normal"

    def register_callback(self, fn):
        self._callbacks.append(fn)

    def start(self):
        if self._running:
            return
        self._running = True
        self._episode_start = time.time()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"[Simulator] Started at {self.sample_rate} Hz")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("[Simulator] Stopped")

    def get_sample(self) -> "SensorReading":
        self._advance_episode()
        return self._make_reading(self._current_level)

    def _loop(self):
        while self._running:
            reading = self.get_sample()
            for cb in self._callbacks:
                try:
                    cb(reading)
                except Exception as e:
                    print(f"[Simulator] Callback error: {e}")
            time.sleep(self._interval)

    def _advance_episode(self):
        duration = self.EPISODE_DURATIONS[self._current_level]
        if time.time() - self._episode_start >= duration:
            self._seq_idx = (self._seq_idx + 1) % len(self.SEQUENCE)
            self._current_level = self.SEQUENCE[self._seq_idx]
            self._episode_start = time.time()
            print(f"[Simulator] Stress -> {self._current_level.upper()}")

    def _make_reading(self, level: str) -> "SensorReading":
        p = self.STRESS_PROFILES[level]
        scores = self.STRESS_SCORES[level]

        def noisy(lo, hi):
            mid = (lo + hi) / 2
            spread = (hi - lo) / 2
            noise = random.gauss(0, spread * self.noise_factor)
            wave = math.sin(time.time() * 0.3) * spread * 0.15
            return max(lo * 0.9, min(hi * 1.1, mid + noise + wave))

        return SensorReading(
            timestamp=time.time(),
            heart_rate=noisy(*p["hr"]),
            gsr=noisy(*p["gsr"]),
            spo2=noisy(*p["spo2"]),
            stress_score=random.uniform(*scores),
        )
