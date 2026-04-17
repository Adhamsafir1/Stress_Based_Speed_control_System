"""
ml/train.py
-----------
Trains a Random Forest classifier on simulated physiological sensor data.

Output: models/stress_model.pkl

Usage:
    python -m ml.train
    python -m ml.train --samples 8000
"""

import argparse
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sensor.simulator import StressSimulator
from ml.preprocessor import SensorBuffer

LABEL_MAP  = {"normal": 0, "mild": 1, "high": 2, "critical": 3}
LABEL_NAMES = ["normal", "mild", "high", "critical"]
MODEL_PATH  = Path("models/stress_model.pkl")


def generate_dataset(n_samples: int = 5000):
    print(f"[Train] Generating {n_samples} labeled samples...")
    sim    = StressSimulator(sample_rate=10.0, noise_factor=0.08)
    buffer = SensorBuffer(window_size=30)
    X, y   = [], []
    t0     = time.time()

    while len(X) < n_samples:
        r = sim.get_sample()
        buffer.push(r)
        feats = buffer.extract_features()
        if feats is not None:
            X.append(feats)
            y.append(LABEL_MAP[sim._current_level])

    print(f"[Train] Done in {time.time() - t0:.1f}s — {len(X)} samples")
    return np.array(X), np.array(y)


def train(n_samples: int = 5000) -> Pipeline:
    X, y = generate_dataset(n_samples)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    RandomForestClassifier(
            n_estimators=150,
            max_depth=14,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1,
        )),
    ])

    print("[Train] Fitting Random Forest...")
    pipeline.fit(X_tr, y_tr)

    y_pred = pipeline.predict(X_te)
    acc    = (y_pred == y_te).mean()
    print(f"[Train] Accuracy: {acc * 100:.1f}%\n")
    print(classification_report(y_te, y_pred, target_names=LABEL_NAMES))

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"[Train] Model saved -> {MODEL_PATH}")
    return pipeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=5000)
    args = parser.parse_args()
    train(args.samples)
