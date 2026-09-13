# Guardian Agent MVP

Guardian Agent is GuardianPaw's high-level interpretation, risk assessment, and human-escalation layer. It consumes a structured robot telemetry snapshot and returns a stable decision containing the situation, risk level, recommendation, human-escalation flag, explanation, and autonomous-patrol permission.

## Why it exists

The ESP32 is deliberately responsible for real-time behavior. A language model is useful for interpreting context and explaining a high-level recommendation, but it must never replace deterministic stopping and obstacle-avoidance logic. Guardian Agent therefore uses two layers:

1. A deterministic safety policy evaluates non-negotiable constraints.
2. A real [Strands Agents SDK](https://strandsagents.com/docs/) `Agent` uses Amazon Bedrock by default to interpret context and produce a structured high-level explanation.

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

The Guardian Agent CLI and deterministic policy run locally. The normal CLI path constructs and invokes a real Strands Agent with a registered custom tool and structured output. Successful Bedrock inference still depends on the machine's AWS credentials, region, model access, and network connectivity.

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

Strands uses Amazon Bedrock by default. Configure AWS credentials through the standard AWS credential chain and ensure the selected model is enabled. `.env.example` lists supported variable names but the program does not load that file or contain secrets. `GUARDIAN_BEDROCK_MODEL_ID` can optionally select a Bedrock model without tying the code to a personal account.

## Run the demo

Real Strands inference path:

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

They cover normal patrol, obstacle handling, sensor fault, disconnection, and rejection of a model response that attempts to relax a hard rule.

## Current limitations

- The telemetry timeline is simulated; physical VL53L1X and D21 / D22 I2C communication are not verified.
- No live ESP32-to-Agent telemetry transport is implemented.
- Battery status is `null` because GuardianPaw has no verified battery telemetry source.
- Model inference requires valid AWS credentials and Bedrock model access.
- Power-system brownout risk remains under hardware investigation; power upgrades are deferred.
- No MPU6050, vision, AgentCore deployment, database, web UI, or multi-agent swarm is included.

## Planned real robot integration

After Phase 1-B verifies the physical VL53L1X, define a read-only telemetry contract between the ESP32 and Guardian Agent. Feed verified state snapshots into the same `RobotState` model, retain ESP32 authority for immediate safety, and expose only constrained high-level task recommendations to any future command bridge. Phase 1-C real-motion avoidance remains a separate, supervised hardware milestone.
