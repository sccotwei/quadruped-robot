"""Deterministic safety rules that the language model cannot override."""

from __future__ import annotations

from .models import AgentDecision, RobotState, SafetyAssessment

ACTIVE_AVOIDANCE_STATES = frozenset(
    {"OBSTACLE_DETECTED", "BACKING_UP", "TURNING"}
)


def evaluate_safety_policy(state: RobotState) -> SafetyAssessment:
    """Evaluate fail-safe rules before any model reasoning occurs."""

    avoidance_state = state.avoidance_state.upper()

    if not state.connected:
        return SafetyAssessment(
            risk_level="high",
            allow_autonomous_patrol=False,
            requires_human=True,
            required_action="Stop the mission and ask a human to restore telemetry connectivity.",
            reason="Robot telemetry is disconnected, so current conditions cannot be trusted.",
        )

    if not state.distance_valid or avoidance_state == "SENSOR_FAULT":
        return SafetyAssessment(
            risk_level="high",
            allow_autonomous_patrol=False,
            requires_human=True,
            required_action="Keep the robot stopped and ask a human to inspect the distance sensor.",
            reason="Distance telemetry is invalid or the local controller reports SENSOR_FAULT.",
        )

    if avoidance_state == "RECOVERING":
        return SafetyAssessment(
            risk_level="medium",
            allow_autonomous_patrol=False,
            requires_human=False,
            required_action="Observe recovery and resume patrol only after the local state returns to CLEAR.",
            reason="The ESP32 local safety controller is still completing recovery.",
        )

    if state.local_safety_engaged or avoidance_state in ACTIVE_AVOIDANCE_STATES:
        return SafetyAssessment(
            risk_level="medium",
            allow_autonomous_patrol=False,
            requires_human=False,
            required_action="Wait for ESP32 local avoidance to complete; do not issue competing motion guidance.",
            reason="The ESP32 local safety controller has priority and is handling an obstacle.",
        )

    if avoidance_state != "CLEAR":
        return SafetyAssessment(
            risk_level="medium",
            allow_autonomous_patrol=False,
            requires_human=True,
            required_action="Pause patrol and ask a human to inspect the unknown avoidance state.",
            reason=f"Avoidance state {avoidance_state!r} is not recognized as safe.",
        )

    return SafetyAssessment(
        risk_level="low",
        allow_autonomous_patrol=True,
        requires_human=False,
        required_action="Continue patrol while monitoring telemetry and local safety state.",
        reason="Telemetry is connected and valid, and the ESP32 reports CLEAR.",
    )


def policy_only_decision(state: RobotState) -> AgentDecision:
    """Create an offline diagnostic decision without claiming model inference."""

    assessment = evaluate_safety_policy(state)
    avoidance_state = state.avoidance_state.upper()

    if not state.connected:
        situation = "GuardianPaw telemetry is disconnected."
    elif not state.distance_valid or avoidance_state == "SENSOR_FAULT":
        situation = "GuardianPaw cannot rely on its current distance telemetry."
    elif avoidance_state == "RECOVERING":
        situation = "The local controller is recovering after avoidance."
    elif state.local_safety_engaged or avoidance_state in ACTIVE_AVOIDANCE_STATES:
        situation = "The ESP32 local safety controller is handling an obstacle."
    else:
        situation = "GuardianPaw has valid telemetry and a clear local safety state."

    return AgentDecision(
        situation=situation,
        risk_level=assessment.risk_level,
        recommended_action=assessment.required_action,
        requires_human=assessment.requires_human,
        reason=assessment.reason,
        allow_autonomous_patrol=assessment.allow_autonomous_patrol,
    )


def enforce_safety_policy(
    candidate: AgentDecision, assessment: SafetyAssessment
) -> AgentDecision:
    """Clamp a model decision to the deterministic safety result."""

    model_reason = candidate.reason.strip()
    reason = assessment.reason
    if model_reason:
        reason = f"{model_reason} Deterministic safety policy: {assessment.reason}"

    return AgentDecision(
        situation=candidate.situation.strip(),
        risk_level=assessment.risk_level,
        recommended_action=assessment.required_action,
        requires_human=assessment.requires_human,
        reason=reason,
        allow_autonomous_patrol=assessment.allow_autonomous_patrol,
    )
