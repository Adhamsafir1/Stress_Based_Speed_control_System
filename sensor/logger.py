import csv
import time
from pathlib import Path
from typing import Optional

from sensor.simulator import SensorReading


class SensorLogger:
    """
    Persists SensorReading objects to rolling CSV log files in the data/ directory.

    Creates a new timestamped file when the current file hits max_rows.
    Thread-safe for concurrent writes.

    Usage:
        logger = SensorLogger(log_dir="data")
        logger.start()
        logger.log(reading)   # called from sensor callback
        logger.stop()
    """

    FIELDNAMES = ["timestamp", "heart_rate", "gsr", "spo2", "stress_score"]

    def __init__(self, log_dir: str = "data", max_rows: int = 10_000):
        self.log_dir = Path(log_dir)
        self.max_rows = max_rows
        self._file = None
        self._writer: Optional[csv.DictWriter] = None
        self._row_count = 0
        self._current_path: Optional[Path] = None

    def start(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._open_file()
        print(f"[Logger] Logging to {self._current_path}")

    def stop(self):
        if self._file:
            self._file.flush()
            self._file.close()
            self._file = None
        print(f"[Logger] Saved {self._row_count} rows -> {self._current_path}")

    def log(self, reading: SensorReading):
        if not self._writer:
            return
        self._writer.writerow(reading.to_dict())
        self._row_count += 1
        if self._row_count >= self.max_rows:
            self.stop()
            self._open_file()

    def _open_file(self):
        ts = time.strftime("%Y%m%d_%H%M%S")
        self._current_path = self.log_dir / f"sensor_log_{ts}.csv"
        self._file = open(self._current_path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.FIELDNAMES)
        self._writer.writeheader()
        self._row_count = 0
