import time
import threading
from typing import Optional, Callable

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("[Reader] pyserial not installed — hardware reading disabled")

from sensor.simulator import SensorReading


class SerialSensorReader:
    """
    Reads physiological sensor data from a hardware device over a serial (COM/USB) port.

    Expected Arduino/ESP32 serial format (CSV per line):
        timestamp,heart_rate,gsr,spo2
        e.g.: 1713345678.123,82.5,3.24,98.5

    Falls back gracefully if the serial port is unavailable.
    """

    def __init__(self, port: str = "COM3", baud_rate: int = 9600, timeout: float = 2.0):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self._serial = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: list[Callable] = []
        self._connected = False

    def register_callback(self, fn: Callable):
        self._callbacks.append(fn)

    def connect(self) -> bool:
        if not SERIAL_AVAILABLE:
            print("[Reader] pyserial not installed")
            return False
        try:
            self._serial = serial.Serial(
                self.port,
                self.baud_rate,
                timeout=self.timeout
            )
            self._connected = True
            print(f"[Reader] Connected to {self.port} @ {self.baud_rate} baud")
            return True
        except Exception as e:
            print(f"[Reader] Connection failed: {e}")
            return False

    def start(self):
        if not self._connected and not self.connect():
            print("[Reader] Cannot start — serial not connected")
            return
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
        print("[Reader] Stopped")

    def _read_loop(self):
        while self._running:
            try:
                raw = self._serial.readline()
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                reading = self._parse(line)
                if reading:
                    for cb in self._callbacks:
                        cb(reading)
            except Exception as e:
                print(f"[Reader] Read error: {e}")
                time.sleep(0.5)

    def _parse(self, line: str) -> Optional[SensorReading]:
        try:
            parts = line.split(",")
            if len(parts) < 4:
                return None
            return SensorReading(
                timestamp=float(parts[0]),
                heart_rate=float(parts[1]),
                gsr=float(parts[2]),
                spo2=float(parts[3]),
            )
        except (ValueError, IndexError) as e:
            print(f"[Reader] Parse error ({e}): {line!r}")
            return None
