from dataclasses import dataclass, field
from typing import Any


@dataclass
class TravelRequest:
    destination: str
    days: int
    travelers: int
    budget_cny: float
    preferences: list[str] = field(default_factory=list)


@dataclass
class DayPlan:
    day: int
    morning: str
    afternoon: str
    evening: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "day": self.day,
            "morning": self.morning,
            "afternoon": self.afternoon,
            "evening": self.evening,
        }

