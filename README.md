# 🚗 Stress-Based Speed Control System

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange?logo=scikit-learn)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A real-time driver stress monitoring system that **automatically regulates vehicle speed** based on physiological signals — keeping roads safer by acting before the driver can react.

---

## 🎯 Problem Statement

Driver fatigue and acute stress are responsible for **over 40% of road accidents** globally. Existing systems rely on driver self-reporting, which is unreliable under stress. This system takes a proactive approach: continuously reading physiological signals and automatically limiting speed when dangerous stress levels are detected.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Driver Monitoring System                  │
│                                                             │
│  ┌────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │  Sensors   │───▶│   Stress     │───▶│    Speed       │  │
│  │            │    │  Detection   │    │  Controller    │  │
│  │ • Heart    │    │              │    │                │  │
│  │   Rate     │    │ • Preprocess │    │ • Smooth       │  │
│  │ • GSR      │    │ • Classify   │    │   Transition   │  │
│  │ • SpO₂     │    │ • Predict    │    │ • Speed Limit  │  │
│  └────────────┘    └──────────────┘    └────────────────┘  │
│         │                 │                     │           │
│         └─────────────────┴─────────────────────┘           │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │  Dashboard  │                          │
│                    │  (Flask +   │                          │
│                    │  SocketIO)  │                          │
│                    └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Project Modules

| Module | Description |
|--------|-------------|
| `sensor/` | Data acquisition — simulation + real serial-port reader |
| `ml/` | Stress classification — rule-based + trained ML model |
| `controller/` | Speed control — smooth transitions + alert management |
| `ui/` | Real-time Flask + SocketIO web dashboard |
| `tests/` | Unit tests for all core modules |

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Adhamsafir1/Stress_Based_Speed_control_System.git
cd Stress_Based_Speed_control_System

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Train the ML model
python -m ml.train

# 4. Run the system
python main.py
```

Then open **http://localhost:5000** in your browser to see the live dashboard.

---

## 📊 Stress → Speed Mapping

| Stress Score | Level    | Speed Limit | Action |
|-------------|----------|-------------|--------|
| 0 – 30      | 🟢 Normal   | 100 km/h    | No action |
| 31 – 60     | 🟡 Mild     | 70 km/h     | Gentle alert |
| 61 – 80     | 🟠 High     | 50 km/h     | Audible alert + speed limit |
| 81 – 100    | 🔴 Critical | 30 km/h     | Emergency limit + navigation to rest stop |

---

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **ML**: scikit-learn (Random Forest)
- **Web UI**: Flask + Flask-SocketIO + Chart.js
- **Sensors**: Heart Rate, GSR (Galvanic Skin Response), SpO₂
- **Hardware**: Simulated by default; Arduino/ESP32 via `--mode serial`

---

## 📁 Project Structure

```
Stress_Based_Speed_control_System/
├── sensor/                 # Data acquisition layer
│   ├── simulator.py        # Realistic stress episode simulator
│   ├── reader.py           # Serial port reader (real hardware)
│   └── logger.py           # CSV data logger
├── ml/                     # Stress detection
│   ├── preprocessor.py     # Sliding window + feature extraction
│   ├── classifier.py       # Rule-based classifier
│   ├── train.py            # ML model training
│   └── predictor.py        # Unified predictor
├── controller/             # Vehicle control logic
│   ├── speed_controller.py # Smooth speed transitions
│   ├── mapping.py          # Stress-to-speed mapping
│   └── alerts.py           # Alert management
├── ui/                     # Web dashboard
│   ├── app.py              # Flask + SocketIO server
│   ├── templates/          # HTML templates
│   └── static/             # CSS + JavaScript
├── tests/                  # Unit tests
├── docs/                   # Documentation + diagrams
├── data/                   # Sensor data logs (CSV)
├── models/                 # Trained model files
├── config.yaml             # System configuration
├── main.py                 # Entry point
└── requirements.txt
```

---

## ⚙️ Configuration

All parameters are in `config.yaml`:

```yaml
sensor:
  mode: "simulation"      # or "serial" for real hardware
  serial_port: "COM3"
  sample_rate_hz: 10

stress_detection:
  method: "ml"            # or "rule_based"

speed_control:
  default_speed: 100
  transition_rate: 5      # km/h per second (gradual deceleration)
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Adham Safir** — [GitHub](https://github.com/Adhamsafir1)