from dataclasses import dataclass


SPEED_LIMITS = {
    "normal":   100,
    "mild":      70,
    "high":      50,
    "critical":  30,
}

LEVEL_COLORS = {
    "normal":   "#22c55e",
    "mild":     "#eab308",
    "high":     "#f97316",
    "critical": "#ef4444",
}

MESSAGES = {
    "normal":   "Drive safely. Stress levels normal.",
    "mild":     "Mild stress detected. Speed reduced to 70 km/h.",
    "high":     "High stress! Speed limited to 50 km/h. Consider taking a break.",
    "critical": "CRITICAL STRESS! Speed limited to 30 km/h. Please pull over safely.",
}


@dataclass
class SpeedRecommendation:
    target_speed: int
    stress_level: str
    stress_score: float
    color: str
    message: str

    def to_dict(self):
        return {
            "target_speed": self.target_speed,
            "stress_level": self.stress_level,
            "stress_score": round(self.stress_score, 1),
            "color":        self.color,
            "message":      self.message,
        }


def get_speed_recommendation(stress_level: str, stress_score: float) -> SpeedRecommendation:
    return SpeedRecommendation(
        target_speed=SPEED_LIMITS.get(stress_level, 100),
        stress_level=stress_level,
        stress_score=stress_score,
        color=LEVEL_COLORS.get(stress_level, "#22c55e"),
        message=MESSAGES.get(stress_level, ""),
    )
