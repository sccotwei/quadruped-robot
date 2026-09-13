"""Strands-backed high-level reasoning with deterministic safety enforcement."""

from __future__ import annotations

import json
import os
from typing import Literal, Optional

from pydantic import BaseModel, Field
from strands import Agent

from .models import AgentDecision, RobotState
from .policies import enforce_safety_policy, evaluate_safety_policy
from .tools import evaluate_safety_policy as evaluate_safety_policy_tool

SYSTEM_PROMPT = """
You are Guardian Agent, GuardianPaw's high-level decision and human-escalation
layer. The ESP32 owns gait, servos, immediate stopping, and local obstacle
avoidance. Never produce servo angles, gait commands, or instructions that
compete with an engaged ESP32 safety controller.

Before reasoning, consult the evaluate_safety_policy tool result recorded for
the current RobotState. Its risk, human-escalation, patrol-permission, and
required-action constraints are authoritative and cannot be relaxed. Explain
the current situation and why the high-level recommendation is appropriate.
Do not claim that simulated telemetry came from physical sensors.
""".strip()


class _ReasonedDecision(BaseModel):
    situation: str = Field(description="Concise interpretation of the telemetry")
    risk_level: Literal["low", "medium", "high"]
    recommended_action: str = Field(description="High-level recommendation only")
    requires_human: bool
    reason: str = Field(description="Plain-language explanation")
    allow_autonomous_patrol: bool


class GuardianAgent:
    """Run Strands reasoning, then re-apply deterministic safety constraints."""

    def __init__(self, model_id: Optional[str] = None) -> None:
        selected_model = model_id or os.getenv("GUARDIAN_BEDROCK_MODEL_ID") or None
        options: dict[str, object] = {
            "name": "guardian_agent",
            "system_prompt": SYSTEM_PROMPT,
            "tools": [evaluate_safety_policy_tool],
            "callback_handler": None,
        }
        if selected_model:
            options["model"] = selected_model

        self._agent = Agent(**options)

    @property
    def tool_names(self) -> list[str]:
        return list(self._agent.tool_names)

    def decide(self, state: RobotState) -> AgentDecision:
        assessment = evaluate_safety_policy(state)

        # Calling through agent.tool proves the registered Strands custom-tool
        # path is exercised and records the authoritative result in history.
        self._agent.tool.evaluate_safety_policy(
            robot_state_json=state.to_json()
        )

        prompt = (
            "Interpret this current GuardianPaw telemetry and produce one "
            "high-level decision. TELEMETRY SOURCE: SIMULATED.\n\n"
            f"RobotState:\n{state.to_json()}\n\n"
            "The deterministic assessment below is authoritative:\n"
            f"{json.dumps(assessment.to_dict(), sort_keys=True)}"
        )
        result = self._agent(prompt, structured_output_model=_ReasonedDecision)
        reasoned = result.structured_output
        if reasoned is None:
            raise RuntimeError("Strands returned no structured decision")

        candidate = AgentDecision(
            situation=reasoned.situation,
            risk_level=reasoned.risk_level,
            recommended_action=reasoned.recommended_action,
            requires_human=reasoned.requires_human,
            reason=reasoned.reason,
            allow_autonomous_patrol=reasoned.allow_autonomous_patrol,
        )
        return enforce_safety_policy(candidate, assessment)

    def close(self) -> None:
        self._agent.cleanup()
