import time
import threading
from dataclasses import dataclass
from collections import deque
from typing import Callable


@dataclass
class Alert:
    timestamp: float
    stress_level: str
    stress_score: float
    message: str
    acknowledged: bool = False

    def to_dict(self):
        return {
            "timestamp":    self.timestamp,
            "time_str":     time.strftime("%H:%M:%S", time.localtime(self.timestamp)),
            "stress_level": self.stress_level,
            "stress_score": round(self.stress_score, 1),
            "message":      self.message,
            "acknowledged": self.acknowledged,
        }


class AlertManager:
    """
    Manages stress alerts with per-level cooldown to prevent notification spam.

    Subscribe to alerts via register_callback().
    Alerts are stored with a rolling history for the dashboard.
    """

    TRIGGER_LEVELS = {"mild", "high", "critical"}

    def __init__(self, cooldown_seconds: float = 30.0, max_history: int = 100):
        self.cooldown             = cooldown_seconds
        self._history: deque      = deque(maxlen=max_history)
        self._last_time: dict     = {}
        self._subscribers: list   = []
        self._lock                = threading.Lock()

    def register_callback(self, fn: Callable):
        self._subscribers.append(fn)

    def process(self, stress_level: str, stress_score: float, message: str):
        if stress_level not in self.TRIGGER_LEVELS:
            return

        with self._lock:
            now  = time.time()
            last = self._last_time.get(stress_level, 0)
            if now - last < self.cooldown:
                return
            alert = Alert(
                timestamp=now,
                stress_level=stress_level,
                stress_score=stress_score,
                message=message,
            )
            self._history.appendleft(alert)
            self._last_time[stress_level] = now

        for fn in self._subscribers:
            try:
                fn(alert)
            except Exception as e:
                print(f"[Alerts] Subscriber error: {e}")

    def get_history(self, limit: int = 20) -> list:
        with self._lock:
            return [a.to_dict() for a in list(self._history)[:limit]]

    def acknowledge_all(self):
        with self._lock:
            for a in self._history:
                a.acknowledged = True
