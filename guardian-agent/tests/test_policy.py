"""Offline tests for GuardianPaw's deterministic safety boundary."""

from __future__ import annotations

import unittest

from guardian_agent.models import AgentDecision, RobotState
from guardian_agent.policies import enforce_safety_policy, evaluate_safety_policy


def state(**overrides: object) -> RobotState:
    values: dict[str, object] = {
        "connected": True,
        "movement_state": "PATROLLING",
        "distance_mm": 800,
        "distance_valid": True,
        "sensor_mode": "simulated",
        "avoidance_state": "CLEAR",
        "local_safety_engaged": False,
        "battery_status": None,
        "timestamp": None,
    }
    values.update(overrides)
    return RobotState(**values)  # type: ignore[arg-type]


class SafetyPolicyTests(unittest.TestCase):
    def test_normal_patrol_is_allowed(self) -> None:
        result = evaluate_safety_policy(state())
        self.assertEqual(result.risk_level, "low")
        self.assertTrue(result.allow_autonomous_patrol)
        self.assertFalse(result.requires_human)

    def test_obstacle_defers_to_local_safety(self) -> None:
        result = evaluate_safety_policy(
            state(
                distance_mm=180,
                avoidance_state="OBSTACLE_DETECTED",
                local_safety_engaged=True,
            )
        )
        self.assertEqual(result.risk_level, "medium")
        self.assertFalse(result.allow_autonomous_patrol)
        self.assertFalse(result.requires_human)
        self.assertIn("do not issue competing", result.required_action)

    def test_sensor_fault_requires_human(self) -> None:
        result = evaluate_safety_policy(
            state(
                distance_mm=None,
                distance_valid=False,
                avoidance_state="SENSOR_FAULT",
                local_safety_engaged=True,
            )
        )
        self.assertEqual(result.risk_level, "high")
        self.assertFalse(result.allow_autonomous_patrol)
        self.assertTrue(result.requires_human)

    def test_disconnected_requires_human(self) -> None:
        result = evaluate_safety_policy(state(connected=False))
        self.assertEqual(result.risk_level, "high")
        self.assertFalse(result.allow_autonomous_patrol)
        self.assertTrue(result.requires_human)

    def test_model_cannot_relax_sensor_fault(self) -> None:
        robot_state = state(
            distance_mm=None,
            distance_valid=False,
            avoidance_state="SENSOR_FAULT",
        )
        unsafe_candidate = AgentDecision(
            situation="A sensor is unavailable.",
            risk_level="low",
            recommended_action="Continue patrol.",
            requires_human=False,
            reason="The model attempted a permissive response.",
            allow_autonomous_patrol=True,
        )

        result = enforce_safety_policy(
            unsafe_candidate, evaluate_safety_policy(robot_state)
        )
        self.assertEqual(result.risk_level, "high")
        self.assertFalse(result.allow_autonomous_patrol)
        self.assertTrue(result.requires_human)
        self.assertNotEqual(result.recommended_action, "Continue patrol.")


if __name__ == "__main__":
    unittest.main()
