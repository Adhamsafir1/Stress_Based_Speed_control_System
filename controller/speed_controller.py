import time
import threading


class SpeedController:
    """
    Manages vehicle speed with smooth, gradual transitions.

    Instead of instantly cutting speed (dangerous), this controller
    adjusts at a configurable rate (km/h per second) towards a target.

    Thread-safe: set_target() can be called from any thread.
    """

    def __init__(
        self,
        initial_speed: float = 60.0,
        max_speed: float = 100.0,
        min_speed: float = 20.0,
        transition_rate: float = 5.0,
    ):
        self.current_speed   = initial_speed
        self.target_speed    = initial_speed
        self.max_speed       = max_speed
        self.min_speed       = min_speed
        self.transition_rate = transition_rate
        self._lock           = threading.Lock()
        self._running        = False
        self._thread         = None

    def set_target(self, target: float):
        with self._lock:
            self.target_speed = max(self.min_speed, min(self.max_speed, target))

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def get_status(self) -> dict:
        with self._lock:
            return {
                "current_speed": round(self.current_speed, 1),
                "target_speed":  round(self.target_speed,  1),
                "at_target":     abs(self.current_speed - self.target_speed) < 0.5,
            }

    def _loop(self):
        dt = 0.1
        while self._running:
            with self._lock:
                diff      = self.target_speed - self.current_speed
                max_delta = self.transition_rate * dt
                if abs(diff) > max_delta:
                    self.current_speed += max_delta * (1 if diff > 0 else -1)
                else:
                    self.current_speed = self.target_speed
            time.sleep(dt)
