"""Offline tests for explicit Guardian Agent model-provider selection."""

from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch, sentinel

from guardian_agent.agent import (
    DEFAULT_BEDROCK_MODEL_ID,
    DEFAULT_OLLAMA_HOST,
    GuardianAgent,
    resolve_model_provider,
)
from guardian_agent.models import RobotState
from guardian_agent.tools import evaluate_safety_policy


class ProviderSelectionTests(unittest.TestCase):
    def test_bedrock_is_default_with_expected_model(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch(
                "guardian_agent.agent.BedrockModel", return_value=sentinel.bedrock_model
            ) as bedrock_model,
            patch("guardian_agent.agent.Agent") as agent,
        ):
            guardian = GuardianAgent()

        bedrock_model.assert_called_once_with(model_id=DEFAULT_BEDROCK_MODEL_ID)
        self.assertEqual(guardian.model_provider, "bedrock")
        self.assertEqual(guardian.model_id, DEFAULT_BEDROCK_MODEL_ID)
        self.assertIsNone(guardian.ollama_host)
        self.assertIs(agent.call_args.kwargs["model"], sentinel.bedrock_model)
        self.assertIn(evaluate_safety_policy, agent.call_args.kwargs["tools"])

    def test_ollama_uses_explicit_environment_configuration(self) -> None:
        environment = {
            "GUARDIAN_MODEL_PROVIDER": "ollama",
            "OLLAMA_HOST": "http://localhost:11434",
            "OLLAMA_MODEL": "test-tool-model",
        }
        with (
            patch.dict(os.environ, environment, clear=True),
            patch(
                "guardian_agent.agent._load_ollama_model_class"
            ) as load_ollama_model,
            patch("guardian_agent.agent.Agent") as agent,
        ):
            ollama_model = load_ollama_model.return_value
            ollama_model.return_value = sentinel.ollama_model
            guardian = GuardianAgent()

        load_ollama_model.assert_called_once_with()
        ollama_model.assert_called_once_with(
            host=DEFAULT_OLLAMA_HOST, model_id="test-tool-model"
        )
        self.assertEqual(guardian.model_provider, "ollama")
        self.assertEqual(guardian.model_id, "test-tool-model")
        self.assertEqual(guardian.ollama_host, DEFAULT_OLLAMA_HOST)
        self.assertIs(agent.call_args.kwargs["model"], sentinel.ollama_model)
        self.assertIn(evaluate_safety_policy, agent.call_args.kwargs["tools"])

    def test_ollama_requires_model_name(self) -> None:
        with patch.dict(
            os.environ, {"GUARDIAN_MODEL_PROVIDER": "ollama"}, clear=True
        ):
            with self.assertRaisesRegex(ValueError, "OLLAMA_MODEL is required"):
                GuardianAgent()

    def test_unknown_provider_is_rejected_without_fallback(self) -> None:
        with self.assertRaisesRegex(ValueError, "bedrock.*ollama"):
            resolve_model_provider("unsupported")

    def test_decision_path_keeps_structured_output_and_post_enforcement(self) -> None:
        state = RobotState(
            connected=True,
            movement_state="STOPPED_BY_LOCAL_SAFETY",
            distance_mm=None,
            distance_valid=False,
            sensor_mode="simulated",
            avoidance_state="SENSOR_FAULT",
            local_safety_engaged=True,
        )
        unsafe_model_output = SimpleNamespace(
            situation="The sensor is unavailable.",
            risk_level="low",
            recommended_action="Continue patrol.",
            requires_human=False,
            reason="The model attempted a permissive response.",
            allow_autonomous_patrol=True,
        )

        with (
            patch.dict(os.environ, {}, clear=True),
            patch(
                "guardian_agent.agent.BedrockModel",
                return_value=sentinel.bedrock_model,
            ),
            patch("guardian_agent.agent.Agent") as agent_class,
        ):
            agent_instance = agent_class.return_value
            agent_instance.return_value = SimpleNamespace(
                structured_output=unsafe_model_output
            )
            guardian = GuardianAgent()
            decision = guardian.decide(state)

        agent_instance.tool.evaluate_safety_policy.assert_called_once_with(
            robot_state_json=state.to_json()
        )
        self.assertEqual(
            agent_instance.call_args.kwargs["structured_output_model"].__name__,
            "_ReasonedDecision",
        )
        self.assertEqual(decision.risk_level, "high")
        self.assertTrue(decision.requires_human)
        self.assertFalse(decision.allow_autonomous_patrol)
        self.assertNotEqual(decision.recommended_action, "Continue patrol.")


if __name__ == "__main__":
    unittest.main()
