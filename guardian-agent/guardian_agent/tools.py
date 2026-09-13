"""Small, read-only tools exposed to the Strands agent."""

from __future__ import annotations

import json
from typing import Any

from strands import tool

from .models import RobotState
from .policies import evaluate_safety_policy as evaluate_policy


@tool
def evaluate_safety_policy(robot_state_json: str) -> dict[str, Any]:
    """Evaluate GuardianPaw's non-negotiable local safety rules.

    Use this tool before making a high-level recommendation. It accepts one
    serialized RobotState JSON object and returns the authoritative risk,
    human-escalation, patrol-permission, and required-action constraints. It
    never controls actuators and has no network or filesystem side effects.

    Args:
        robot_state_json: JSON object matching the RobotState telemetry contract.
    """

    payload = json.loads(robot_state_json)
    if not isinstance(payload, dict):
        raise ValueError("robot_state_json must decode to an object")
    state = RobotState.from_mapping(payload)
    return evaluate_policy(state).to_dict()
