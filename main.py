"""
main.py
-------
Stress-Based Speed Control System — Entry Point

Wires together:
    Sensor -> Preprocessor -> Predictor -> SpeedController -> Dashboard

Usage:
    python main.py               # Full system with web dashboard
    python main.py --no-ui       # Console only (no browser)
    python main.py --mode serial # Use real serial sensor hardware
"""

import argparse
import sys
import time
import threading

import yaml

from sensor.simulator import StressSimulator
from sensor.reader import SerialSensorReader
from sensor.logger import SensorLogger
from ml.predictor import StressPredictor
from controller.speed_controller import SpeedController
from controller.mapping import get_speed_recommendation
from controller.alerts import AlertManager


def load_config(path: str = "config.yaml") -> dict:
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"[Main] {path} not found — using defaults")
        return {}


def run(config: dict, with_ui: bool = True):
    sensor_cfg = config.get("sensor", {})
    ctrl_cfg   = config.get("speed_control", {})
    alert_cfg  = config.get("alerts", {})
    dash_cfg   = config.get("dashboard", {})

    # ── Sensor Source ──────────────────────────────────────
    mode = sensor_cfg.get("mode", "simulation")
    if mode == "serial":
        source = SerialSensorReader(
            port=sensor_cfg.get("serial_port", "COM3"),
            baud_rate=sensor_cfg.get("baud_rate", 9600),
        )
        if not source.connect():
            print("[Main] Serial unavailable — falling back to simulation")
            source = StressSimulator(sample_rate=sensor_cfg.get("sample_rate_hz", 10))
    else:
        source = StressSimulator(sample_rate=sensor_cfg.get("sample_rate_hz", 10))

    # ── Core Components ────────────────────────────────────
    logger     = SensorLogger(log_dir="data")
    predictor  = StressPredictor(
        model_path=config.get("stress_detection", {}).get("model_path", "models/stress_model.pkl")
    )
    speed_ctrl = SpeedController(
        initial_speed=60.0,
        max_speed=ctrl_cfg.get("limits", {}).get("normal", 100),
        min_speed=ctrl_cfg.get("min_speed", 20),
        transition_rate=ctrl_cfg.get("transition_rate", 5),
    )
    alert_mgr = AlertManager(
        cooldown_seconds=alert_cfg.get("cooldown_seconds", 30)
    )
    alert_mgr.register_callback(
        lambda a: print(f"\n  [!] {a.stress_level.upper()}: {a.message}")
    )

    # ── Dashboard Thread ───────────────────────────────────
    update_state = None
    if with_ui:
        from ui.app import run_dashboard, update_state as _upd
        update_state = _upd
        dash_thread = threading.Thread(
            target=run_dashboard,
            kwargs={"host": dash_cfg.get("host", "0.0.0.0"),
                    "port": dash_cfg.get("port", 5000)},
            daemon=True,
        )
        dash_thread.start()
        time.sleep(1.5)

    # ── Start ──────────────────────────────────────────────
    logger.start()
    speed_ctrl.start()
    source.start()

    port = dash_cfg.get("port", 5000)
    print("\n" + "=" * 56)
    print("  Stress-Based Speed Control System  —  RUNNING")
    print("=" * 56)
    if with_ui:
        print(f"  Dashboard  :  http://localhost:{port}")
    print("  Mode       : ", mode)
    print("  Press Ctrl+C to stop")
    print("=" * 56 + "\n")

    try:
        while True:
            reading = source.get_sample()
            logger.log(reading)

            result = predictor.predict(reading)
            if result is not None:
                rec          = get_speed_recommendation(result.stress_level, result.stress_score)
                speed_status = speed_ctrl.get_status()

                speed_ctrl.set_target(rec.target_speed)
                alert_mgr.process(result.stress_level, result.stress_score, rec.message)

                # Console progress bar
                filled = int(result.stress_score / 5)
                bar    = "█" * filled + "░" * (20 - filled)
                print(
                    f"\r  [{result.stress_level.upper():8s}] "
                    f"Score:{result.stress_score:5.1f} |{bar}| "
                    f"Speed {speed_status['current_speed']:5.1f} -> {speed_status['target_speed']:3.0f} km/h  ",
                    end="", flush=True,
                )

                if with_ui and update_state:
                    update_state(
                        sensor_data=reading.to_dict(),
                        stress_data={**result.to_dict(), "message": rec.message},
                        speed_data=speed_status,
                        alerts=alert_mgr.get_history(),
                    )

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n[Main] Shutting down...")
    finally:
        source.stop()
        logger.stop()
        speed_ctrl.stop()
        print("[Main] Stopped cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Stress-Based Speed Control System")
    parser.add_argument("--no-ui", action="store_true", help="Run without web dashboard")
    parser.add_argument("--mode", choices=["simulation", "serial"], default=None,
                        help="Sensor mode override")
    args = parser.parse_args()

    cfg = load_config()
    if args.mode:
        cfg.setdefault("sensor", {})["mode"] = args.mode

    run(cfg, with_ui=not args.no_ui)


if __name__ == "__main__":
    main()
