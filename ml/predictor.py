from pathlib import Path
from typing import Optional

import joblib
import numpy as np

from ml.classifier import RuleBasedClassifier, ClassificationResult
from ml.preprocessor import SensorBuffer, SignalNormalizer
from sensor.simulator import SensorReading

LABEL_NAMES = {0: "normal", 1: "mild", 2: "high", 3: "critical"}


class StressPredictor:
    """
    Unified stress predictor.

    Attempts to load a trained sklearn model from disk.
    If unavailable, falls back to the rule-based classifier transparently.

    Usage:
        predictor = StressPredictor()
        result = predictor.predict(reading)   # returns ClassificationResult or None
    """

    def __init__(
        self,
        model_path: str = "models/stress_model.pkl",
        window_size: int = 30,
        use_ml: bool = True,
    ):
        self.buffer = SensorBuffer(window_size=window_size)
        self._model = None
        self._mode  = "rule_based"

        if use_ml:
            self._load_model(model_path)

    def predict(self, reading: SensorReading) -> Optional[ClassificationResult]:
        reading = SignalNormalizer.clip_outliers(reading)
        self.buffer.push(reading)

        if self._mode == "ml" and self._model is not None:
            return self._ml_predict(reading)
        return RuleBasedClassifier.classify(reading)

    def _load_model(self, path: str):
        p = Path(path)
        if not p.exists():
            print("[Predictor] No model found — using rule-based classifier")
            return
        try:
            self._model = joblib.load(p)
            self._mode  = "ml"
            print(f"[Predictor] Loaded ML model from {p}")
        except Exception as e:
            print(f"[Predictor] Model load failed ({e}) — rule-based fallback")

    def _ml_predict(self, reading: SensorReading) -> Optional[ClassificationResult]:
        feats = self.buffer.extract_features()
        if feats is None:
            return RuleBasedClassifier.classify(reading)
        try:
            proba = self._model.predict_proba(feats.reshape(1, -1))[0]
            label = int(np.argmax(proba))
            level = LABEL_NAMES[label]
            score = float(proba[0] * 15 + proba[1] * 45 + proba[2] * 70 + proba[3] * 90)
            return ClassificationResult(
                stress_score=score,
                stress_level=level,
                hr_score=reading.heart_rate,
                gsr_score=reading.gsr,
                spo2_score=reading.spo2,
                confidence=float(proba[label]),
            )
        except Exception as e:
            print(f"[Predictor] ML inference error ({e}) — falling back to rules")
            return RuleBasedClassifier.classify(reading)
