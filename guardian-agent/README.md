# Guardian Agent MVP

Guardian Agent is GuardianPaw's high-level interpretation, risk assessment, and human-escalation layer. It consumes a structured robot telemetry snapshot and returns a stable decision containing the situation, risk level, recommendation, human-escalation flag, explanation, and autonomous-patrol permission.

## Why it exists

The ESP32 is deliberately responsible for real-time behavior. A language model is useful for interpreting context and explaining a high-level recommendation, but it must never replace deterministic stopping and obstacle-avoidance logic. Guardian Agent therefore uses two layers:

1. A deterministic safety policy evaluates non-negotiable constraints.
2. A real [Strands Agents SDK](https://strandsagents.com/docs/) `Agent` uses Amazon Bedrock by default, with an explicit Ollama local-provider fallback, to interpret context and produce a structured high-level explanation.

The deterministic result is enforced again after model inference, so the model cannot relax risk, human escalation, patrol permission, or the required safe action.

## Responsibility boundary

```text
Sensors / telemetry
        |
        v
ESP32 local safety controller
        |
        v
Guardian Agent (Strands high-level reasoning)
        |
        v
High-level recommendation / human escalation
```

- ESP32: gait, servos, local obstacle avoidance, immediate safety stop, and low-level motion.
- Guardian Agent: telemetry interpretation, high-level risk, task-continuation recommendation, and human escalation.
- Guardian Agent does not send servo angles, implement gait, or override an engaged ESP32 safety controller.

## Current MVP status

Real and verified project capabilities:

- Physical quadruped locomotion
- ESP32 firmware
- Wi-Fi / HTTP control
- Phase 1-A avoidance state machine running on a real ESP32
- Dry Run isolation preventing avoidance-controller actuator calls

The Guardian Agent CLI and deterministic policy run locally. The normal CLI path constructs and invokes a real Strands Agent with a registered custom tool and structured output. Amazon Bedrock remains the preferred/default provider. An explicit Ollama provider lets judges and developers run the same Strands path locally without AWS credentials. Live local Strands inference has been verified with Ollama and `llama3.1`; provider selection never bypasses the deterministic policy.

## Simulation disclosure

The demo always prints `TELEMETRY SOURCE: SIMULATED`. Its ToF values are simulated and do not prove that a physical VL53L1X is connected or verified. The project does not currently claim MPU6050 integration or computer vision.

## Installation

Python 3.10 or newer is recommended.

```text
cd guardian-agent
python -m venv .venv
```

Windows PowerShell:

```text
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS / Linux:

```text
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The Ollama integration uses the official Strands optional dependency already declared in `requirements.txt`. To add it to an existing environment directly:

```text
python -m pip install 'strands-agents[ollama]>=1.55,<2'
```

## Model providers

Provider selection is explicit. The application never falls back from Bedrock to Ollama automatically, so a failed cloud request cannot be mistaken for a successful local request.

### Amazon Bedrock — preferred and default

If `GUARDIAN_MODEL_PROVIDER` is absent, Guardian Agent creates Strands' `BedrockModel` with `global.anthropic.claude-sonnet-4-6`. `GUARDIAN_BEDROCK_MODEL_ID` can override that model without tying the code to a personal account. Configure AWS credentials through the standard credential chain and ensure the selected model is available.

Windows PowerShell:

```text
$env:GUARDIAN_MODEL_PROVIDER="bedrock"
python demo.py
```

Amazon Bedrock live inference is pending AWS account/payment activation.

### Ollama — explicit local fallback

Install [Ollama](https://ollama.com/download), pull a model that supports tool calling and structured output, and ensure its local server is running. The model is never hard-coded: `OLLAMA_MODEL` is required. `OLLAMA_HOST` defaults to `http://localhost:11434`.

Example setup:

```text
ollama pull llama3.1
ollama serve
```

Windows PowerShell:

```text
$env:GUARDIAN_MODEL_PROVIDER="ollama"
$env:OLLAMA_MODEL="llama3.1"
python demo.py
```

macOS / Linux:

```text
GUARDIAN_MODEL_PROVIDER=ollama OLLAMA_MODEL=llama3.1 python demo.py
```

The model name above matches the verified configuration. On Windows, Ollama 0.34.0 with `llama3.1:latest` completed all four GuardianPaw scenarios with exit code 0 in approximately 28.85 seconds. The run used real Strands inference, the registered `evaluate_safety_policy` tool, Pydantic structured output, and deterministic post-enforcement. It produced no validation errors or OOM, and Ollama reported NVIDIA RTX 4060 Laptop GPU use.

Ollama emitted a non-fatal warning that forced `ToolChoice` is unsupported. GuardianPaw does not depend on forced provider-side tool choice for its safety boundary: `GuardianAgent.decide()` explicitly invokes the registered `evaluate_safety_policy` tool before model reasoning, then enforces the same deterministic assessment after the structured response.

## Run the demo

Real Strands inference path, after configuring one provider above:

```text
python demo.py
```

Offline deterministic fallback/debug path:

```text
python demo.py --policy-only
```

`--policy-only` explicitly reports that no model inference occurred. It is useful when AWS access is unavailable, but it is not a substitute for the real Strands path in the final hackathon demonstration.

## Expected demo scenarios

| Scenario | Expected safety result |
|---|---|
| Normal patrol | Low risk; autonomous patrol allowed; no human required |
| Obstacle approaching | Medium risk; ESP32 local safety retains control; wait without competing |
| Recovery | Medium risk; observe recovery and resume only after `CLEAR` |
| Sensor fault | High risk; autonomous patrol denied; human required |

## Tests

The safety tests are fully offline and do not call Bedrock:

```text
python -m unittest discover -s tests -v
```

They cover normal patrol, obstacle handling, sensor fault, disconnection, rejection of a model response that attempts to relax a hard rule, Bedrock defaults, Ollama configuration, custom-tool registration, and rejection of unknown providers.

## Current limitations

- The telemetry timeline is simulated; physical VL53L1X and D21 / D22 I2C communication are not verified.
- No live ESP32-to-Agent telemetry transport is implemented.
- Battery status is `null` because GuardianPaw has no verified battery telemetry source.
- Bedrock inference requires valid AWS credentials and model access; live verification is pending account/payment activation.
- Ollama inference requires a separately installed/running Ollama service and a pulled `llama3.1` model. Live local verification succeeded, with the non-fatal forced-`ToolChoice` limitation disclosed above.
- Power-system brownout risk remains under hardware investigation; power upgrades are deferred.
- No MPU6050, vision, AgentCore deployment, database, web UI, or multi-agent swarm is included.

## Planned real robot integration

After Phase 1-B verifies the physical VL53L1X, define a read-only telemetry contract between the ESP32 and Guardian Agent. Feed verified state snapshots into the same `RobotState` model, retain ESP32 authority for immediate safety, and expose only constrained high-level task recommendations to any future command bridge. Phase 1-C real-motion avoidance remains a separate, supervised hardware milestone.
