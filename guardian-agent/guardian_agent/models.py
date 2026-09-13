"""Data contracts shared by telemetry, safety policy, and the agent."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping, Optional

RiskLevel = Literal["low", "medium", "high"]
SensorMode = Literal["simulated", "hardware"]


@dataclass(frozen=True)
class RobotState:
    """A high-level snapshot; it contains no direct actuator commands."""

    connected: bool
    movement_state: str
    distance_mm: Optional[int]
    distance_valid: bool
    sensor_mode: SensorMode
    avoidance_state: str
    local_safety_engaged: bool
    battery_status: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self) -> None:
        if type(self.connected) is not bool:
            raise TypeError("connected must be a bool")
        if type(self.distance_valid) is not bool:
            raise TypeError("distance_valid must be a bool")
        if type(self.local_safety_engaged) is not bool:
            raise TypeError("local_safety_engaged must be a bool")
        if not self.movement_state.strip():
            raise ValueError("movement_state must not be empty")
        if not self.avoidance_state.strip():
            raise ValueError("avoidance_state must not be empty")
        if self.sensor_mode not in ("simulated", "hardware"):
            raise ValueError("sensor_mode must be simulated or hardware")
        if self.distance_mm is not None:
            if type(self.distance_mm) is not int:
                raise TypeError("distance_mm must be an int or None")
            if self.distance_mm < 0:
                raise ValueError("distance_mm must not be negative")
        if self.distance_valid and self.distance_mm is None:
            raise ValueError("valid distance telemetry requires distance_mm")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "RobotState":
        """Validate a decoded telemetry mapping."""

        required = (
            "connected",
            "movement_state",
            "distance_mm",
            "distance_valid",
            "sensor_mode",
            "avoidance_state",
            "local_safety_engaged",
        )
        missing = [name for name in required if name not in value]
        if missing:
            raise ValueError(f"missing RobotState fields: {', '.join(missing)}")

        return cls(
            connected=value["connected"],
            movement_state=value["movement_state"],
            distance_mm=value["distance_mm"],
            distance_valid=value["distance_valid"],
            sensor_mode=value["sensor_mode"],
            avoidance_state=value["avoidance_state"],
            local_safety_engaged=value["local_safety_engaged"],
            battery_status=value.get("battery_status"),
            timestamp=value.get("timestamp"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


@dataclass(frozen=True)
class SafetyAssessment:
    """Non-negotiable output from the deterministic safety layer."""

    risk_level: RiskLevel
    allow_autonomous_patrol: bool
    requires_human: bool
    required_action: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentDecision:
    """Stable decision contract printed by the demo and future integrations."""

    situation: str
    risk_level: RiskLevel
    recommended_action: str
    requires_human: bool
    reason: str
    allow_autonomous_patrol: bool

    def __post_init__(self) -> None:
        if self.risk_level not in ("low", "medium", "high"):
            raise ValueError("risk_level must be low, medium, or high")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
