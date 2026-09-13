"""Strands-backed high-level reasoning with deterministic safety enforcement."""

from __future__ import annotations

import json
import os
from typing import Literal, Optional, cast

from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel

from .models import AgentDecision, RobotState
from .policies import enforce_safety_policy, evaluate_safety_policy
from .tools import evaluate_safety_policy as evaluate_safety_policy_tool

ModelProvider = Literal["bedrock", "ollama"]

DEFAULT_MODEL_PROVIDER: ModelProvider = "bedrock"
DEFAULT_BEDROCK_MODEL_ID = "global.anthropic.claude-sonnet-4-6"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"

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


def _environment_value(name: str) -> Optional[str]:
    value = os.getenv(name)
    if value is None:
        return None
    return value.strip() or None


def resolve_model_provider(provider: Optional[str] = None) -> ModelProvider:
    """Resolve an explicit provider without silently falling back."""

    selected = (
        provider or _environment_value("GUARDIAN_MODEL_PROVIDER") or DEFAULT_MODEL_PROVIDER
    ).strip().lower()
    if selected not in ("bedrock", "ollama"):
        raise ValueError(
            "GUARDIAN_MODEL_PROVIDER must be 'bedrock' or 'ollama'; "
            f"got {selected!r}"
        )
    return cast(ModelProvider, selected)


def _load_ollama_model_class() -> type:
    try:
        from strands.models.ollama import OllamaModel
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Strands Ollama support is not installed. Run: "
            "python -m pip install 'strands-agents[ollama]>=1.55,<2'"
        ) from exc
    return OllamaModel


def _create_model(
    provider: ModelProvider, model_id: Optional[str]
) -> tuple[object, str, Optional[str]]:
    if provider == "bedrock":
        selected_model = (
            model_id
            or _environment_value("GUARDIAN_BEDROCK_MODEL_ID")
            or DEFAULT_BEDROCK_MODEL_ID
        )
        return BedrockModel(model_id=selected_model), selected_model, None

    selected_model = model_id or _environment_value("OLLAMA_MODEL")
    if selected_model is None:
        raise ValueError(
            "OLLAMA_MODEL is required when GUARDIAN_MODEL_PROVIDER=ollama. "
            "Pull a tool-capable model and set OLLAMA_MODEL to its name."
        )

    ollama_host = _environment_value("OLLAMA_HOST") or DEFAULT_OLLAMA_HOST
    ollama_model_class = _load_ollama_model_class()

    return (
        ollama_model_class(host=ollama_host, model_id=selected_model),
        selected_model,
        ollama_host,
    )


class GuardianAgent:
    """Run Strands reasoning, then re-apply deterministic safety constraints."""

    def __init__(
        self, model_id: Optional[str] = None, provider: Optional[str] = None
    ) -> None:
        self._model_provider = resolve_model_provider(provider)
        model, self._model_id, self._ollama_host = _create_model(
            self._model_provider, model_id
        )
        options: dict[str, object] = {
            "name": "guardian_agent",
            "system_prompt": SYSTEM_PROMPT,
            "tools": [evaluate_safety_policy_tool],
            "callback_handler": None,
            "model": model,
        }

        self._agent = Agent(**options)

    @property
    def model_provider(self) -> ModelProvider:
        return self._model_provider

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def ollama_host(self) -> Optional[str]:
        return self._ollama_host

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
