"""CLI demonstration for GuardianPaw's high-level Guardian Agent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Optional

from guardian_agent.models import AgentDecision, RobotState
from guardian_agent.policies import policy_only_decision


@dataclass(frozen=True)
class Scenario:
    name: str
    state: RobotState


SCENARIOS = (
    Scenario(
        "Normal patrol",
        RobotState(
            connected=True,
            movement_state="PATROLLING",
            distance_mm=800,
            distance_valid=True,
            sensor_mode="simulated",
            avoidance_state="CLEAR",
            local_safety_engaged=False,
            battery_status=None,
            timestamp="2026-09-11T20:00:00Z",
        ),
    ),
    Scenario(
        "Obstacle approaching",
        RobotState(
            connected=True,
            movement_state="STOPPED_BY_LOCAL_SAFETY",
            distance_mm=180,
            distance_valid=True,
            sensor_mode="simulated",
            avoidance_state="OBSTACLE_DETECTED",
            local_safety_engaged=True,
            battery_status=None,
            timestamp="2026-09-11T20:00:01Z",
        ),
    ),
    Scenario(
        "Recovery",
        RobotState(
            connected=True,
            movement_state="RECOVERING",
            distance_mm=600,
            distance_valid=True,
            sensor_mode="simulated",
            avoidance_state="RECOVERING",
            local_safety_engaged=True,
            battery_status=None,
            timestamp="2026-09-11T20:00:02Z",
        ),
    ),
    Scenario(
        "Sensor fault",
        RobotState(
            connected=True,
            movement_state="STOPPED_BY_LOCAL_SAFETY",
            distance_mm=None,
            distance_valid=False,
            sensor_mode="simulated",
            avoidance_state="SENSOR_FAULT",
            local_safety_engaged=True,
            battery_status=None,
            timestamp="2026-09-11T20:00:03Z",
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--policy-only",
        action="store_true",
        help="Run the offline deterministic pipeline without model inference.",
    )
    parser.add_argument(
        "--model-id",
        help="Optional model ID override for the explicitly selected provider.",
    )
    return parser.parse_args()


def run_strands(state: RobotState, model_id: Optional[str]) -> AgentDecision:
    # Delayed import keeps --policy-only usable without SDK installation.
    from guardian_agent.agent import GuardianAgent

    guardian = GuardianAgent(model_id=model_id)
    try:
        return guardian.decide(state)
    finally:
        guardian.close()


def main() -> int:
    args = parse_args()
    selected_provider = (
        os.getenv("GUARDIAN_MODEL_PROVIDER", "bedrock").strip().lower() or "bedrock"
    )
    print("TELEMETRY SOURCE: SIMULATED", flush=True)
    if args.policy_only:
        print(
            "DECISION PIPELINE: DETERMINISTIC POLICY ONLY (NO MODEL INFERENCE)",
            flush=True,
        )
    else:
        print(
            "DECISION PIPELINE: STRANDS AGENT + DETERMINISTIC SAFETY POLICY",
            flush=True,
        )
        print(f"MODEL PROVIDER: {selected_provider.upper()}", flush=True)

    for index, scenario in enumerate(SCENARIOS, start=1):
        print(f"\n=== Scenario {index}: {scenario.name} ===")
        print("TELEMETRY:")
        print(
            json.dumps(scenario.state.to_dict(), indent=2, sort_keys=True),
            flush=True,
        )

        try:
            decision = (
                policy_only_decision(scenario.state)
                if args.policy_only
                else run_strands(scenario.state, args.model_id)
            )
        except Exception as exc:  # Show a real provider/credential blocker.
            print("STRANDS INFERENCE: NOT VERIFIED", file=sys.stderr)
            print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
            if selected_provider == "bedrock":
                print(
                    "Amazon Bedrock is the default provider. Configure AWS/Bedrock "
                    "access, or explicitly set GUARDIAN_MODEL_PROVIDER=ollama and "
                    "OLLAMA_MODEL to use the local Strands provider. No automatic "
                    "fallback was attempted.",
                    file=sys.stderr,
                )
            elif selected_provider == "ollama":
                print(
                    "Install and start Ollama, pull a tool-capable model, and set "
                    "OLLAMA_MODEL. The offline debug path remains available with "
                    "python demo.py --policy-only.",
                    file=sys.stderr,
                )
            else:
                print(
                    "Set GUARDIAN_MODEL_PROVIDER to bedrock or ollama.",
                    file=sys.stderr,
                )
            return 2

        print("DECISION:")
        print(decision.to_json())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
