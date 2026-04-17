# Architecture Overview

## System Diagram

```
+-------------------------------------------------------------+
|                 Driver Monitoring System                    |
|                                                             |
|  +-----------+    +---------------+    +----------------+  |
|  |  Sensors  |--> | Stress        |--> | Speed          |  |
|  |           |    | Detection     |    | Controller     |  |
|  | Heart Rate|    |               |    |                |  |
|  | GSR (skin)|    | 1. Preprocess |    | Set target     |  |
|  | SpO2      |    | 2. Classify   |    | Smooth slide   |  |
|  +-----------+    | 3. Predict    |    | Alert system   |  |
|       |           +---------------+    +----------------+  |
|       |                  |                     |           |
|       +------------------+---------------------+           |
|                          |                                 |
|                   +------v------+                          |
|                   |  Dashboard  |                          |
|                   |  Flask +    |                          |
|                   |  SocketIO   |                          |
|                   +-------------+                          |
+-------------------------------------------------------------+
```

## Data Flow

```
1. Sensor generates reading every 100ms
       |
2. SensorBuffer accumulates 30 readings (3-second window)
       |
3. StressPredictor extracts 18 features and classifies stress
       |
4. SpeedRecommendation maps stress level to speed limit
       |
5. SpeedController smoothly transitions to new target speed
       |
6. AlertManager fires notifications (with cooldown) on high stress
       |
7. Dashboard receives update via SocketIO and renders in real-time
```

## Module Responsibilities

### sensor/

| File | Purpose |
|------|---------|
| `simulator.py` | Generates realistic physiological data with stress episodes |
| `reader.py` | Reads from real hardware via serial port (Arduino/ESP32) |
| `logger.py` | Persists readings to timestamped CSV files |

### ml/

| File | Purpose |
|------|---------|
| `preprocessor.py` | 30-sample sliding window buffer + 18-feature extraction |
| `classifier.py` | Rule-based stress classification (no training required) |
| `train.py` | Random Forest training pipeline on simulated data |
| `predictor.py` | Unified predictor (ML model or rule-based fallback) |

### controller/

| File | Purpose |
|------|---------|
| `mapping.py` | Stress level -> speed limit + color + message |
| `speed_controller.py` | Smooth speed transitions at configurable rate |
| `alerts.py` | Per-level cooldown alert manager with subscriber pattern |

### ui/

| File | Purpose |
|------|---------|
| `app.py` | Flask + SocketIO server with REST API |
| `templates/index.html` | Single-page dashboard HTML |
| `static/css/style.css` | Dark-theme responsive dashboard styles |
| `static/js/app.js` | WebSocket client + Chart.js real-time rendering |

## Stress -> Speed Mapping

| Stress Score | Level    | Speed Limit |
|-------------|----------|-------------|
| 0 - 30      | Normal   | 100 km/h    |
| 31 - 60     | Mild     | 70 km/h     |
| 61 - 80     | High     | 50 km/h     |
| 81 - 100    | Critical | 30 km/h     |

## Feature Vector (18 dimensions)

For each of the 3 sensor channels [HR, GSR, SpO2]:
- Mean over 30-sample window
- Standard deviation
- Minimum value
- Maximum value
- Linear slope (trend direction)
- Range (max - min)

Total: 6 statistics x 3 channels = **18 features**
