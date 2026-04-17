import time
import threading

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

_state = {
    "sensor":  {},
    "stress":  {},
    "speed":   {},
    "alerts":  [],
    "running": False,
}

app      = Flask(__name__)
app.config["SECRET_KEY"] = "sbscs-2024"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


def update_state(sensor_data: dict, stress_data: dict, speed_data: dict, alerts: list):
    """Called by the main loop on each sensor tick to push state to all clients."""
    _state["sensor"]  = sensor_data
    _state["stress"]  = stress_data
    _state["speed"]   = speed_data
    _state["alerts"]  = alerts
    _state["running"] = True

    socketio.emit("update", {
        "sensor":    sensor_data,
        "stress":    stress_data,
        "speed":     speed_data,
        "alerts":    alerts[:10],
        "timestamp": time.time(),
    })


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    return jsonify(_state)


@app.route("/api/alerts")
def api_alerts():
    return jsonify({"alerts": _state["alerts"]})


@socketio.on("connect")
def on_connect():
    print("[Dashboard] Client connected")
    socketio.emit("update", _state)


@socketio.on("disconnect")
def on_disconnect():
    print("[Dashboard] Client disconnected")


def run_dashboard(host: str = "0.0.0.0", port: int = 5000):
    print(f"[Dashboard] http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=False)
