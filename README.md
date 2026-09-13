# GuardianPaw

GuardianPaw is an embodied home-safety agent that combines a physical quadruped robot, deterministic edge safety, and a Strands-based high-level decision agent.

> Hackathon submission snapshot: the physical ESP32 locomotion baseline, Phase 1-A simulated-sensor safety flow, and live local Strands inference with Ollama are verified. Physical ToF ranging and live Amazon Bedrock inference are explicitly not yet verified.

## The Problem

A home robot is only useful when people do not have to supervise every movement. It must react to immediate hazards locally, continue ordinary tasks when conditions are trustworthy, and ask for help when the available telemetry is no longer safe to rely on.

Putting perception, motion, and language-model reasoning into one control loop makes that boundary difficult to understand and test. GuardianPaw separates the fast, deterministic safety controller from the slower agent that interprets context and communicates a high-level recommendation.

## Architecture at a Glance

```text
Environment / telemetry
        |
        v
ESP32 local safety controller
        |
        v
RobotState -> deterministic safety policy -> Strands Agent
                                                |
                                                v
                       high-level recommendation / human escalation
```

The ESP32 retains authority over physical safety. The model may interpret and explain state, but it cannot override deterministic constraints. See the [submission architecture](docs/SUBMISSION_ARCHITECTURE.md) for the complete edge, policy, custom-tool, and model flow.

## Current MVP Status

| Evidence class | Current scope |
|---|---|
| **REAL / VERIFIED** | Physical locomotion; ESP32 Wi-Fi/HTTP; Phase 1-A state machine on a real ESP32; Dry Run isolation; Strands Agent code with explicit provider selection; deterministic safety policy; custom Strands tool; four-scenario policy-only demo; live local Strands inference using Ollama and llama3.1. |
| **SIMULATED** | Current ToF distance telemetry used by Phase 1-A and the Guardian Agent CLI. |
| **PENDING** | Real VL53L1X ranging; physical autonomous avoidance; MPU6050; vision; live Amazon Bedrock inference. |

## Simulation Disclosure

**The current hackathon demo uses simulated ToF telemetry.**

- The ESP32 software executes on real hardware.
- Obstacle state transitions were verified on the physical ESP32.
- The ToF distance values used in Phase 1-A are simulated.
- The Guardian Agent demo currently consumes simulated telemetry.
- Real VL53L1X integration remains planned Phase 1-B work.

No output in this repository should be interpreted as proof of physical VL53L1X, MPU6050, or vision integration.

## Verification Matrix

| Status | Capability | Evidence and boundary |
|---|---|---|
| **REAL / VERIFIED** | Physical quadruped robot | Existing robot platform is able to perform its baseline locomotion. |
| **REAL / VERIFIED** | ESP32 locomotion baseline | Existing gait, servo GPIO, and motion routines run on the physical ESP32. |
| **REAL / VERIFIED** | Wi-Fi / HTTP control | ESP32 WebServer accepts the existing browser control commands. |
| **REAL / VERIFIED** | Obstacle-avoidance state machine | `CLEAR -> OBSTACLE_DETECTED -> BACKING_UP -> TURNING -> RECOVERING -> CLEAR` is implemented. |
| **REAL / VERIFIED** | Phase 1-A on real ESP32 | The simulated ToF stream and complete state cycle were observed over Serial on physical hardware. |
| **REAL / VERIFIED** | Actuator Dry Run isolation | With Dry Run enabled, avoidance-controller actions produced logs without actuator calls. |
| **REAL / VERIFIED** | Guardian Agent built with Strands Agents SDK | The MVP instantiates a real `strands.Agent`; Bedrock remains the default and an explicit Ollama local-provider path is available. |
| **REAL / VERIFIED** | Deterministic safety policy | Offline rules deny patrol on invalid telemetry, sensor fault, or disconnection and retain priority after model output. |
| **REAL / VERIFIED** | Strands custom tool execution | The read-only `evaluate_safety_policy` function is registered with Strands using `@tool` and its explicit Strands tool invocation completed successfully. |
| **REAL / VERIFIED** | Four-scenario policy-only demo | Normal patrol, obstacle, recovery, and sensor-fault scenarios run without hardware or paid model access. |
| **REAL / VERIFIED** | Live local Strands inference | Ollama 0.34.0 with `llama3.1:latest` completed all four scenarios on Windows with exit code 0 in approximately 28.85 seconds. Pydantic structured output and deterministic post-enforcement succeeded without validation errors or OOM; Ollama reported NVIDIA RTX 4060 Laptop GPU use. |
| **NOT YET VERIFIED** | Real VL53L1X ranging | Phase 1-A uses simulated distance values; Phase 1-B hardware work is pending. |
| **NOT YET VERIFIED** | Real MPU6050 | No MPU6050 integration is implemented. |
| **NOT YET VERIFIED** | Vision | No vision input or vision model is implemented. |
| **NOT YET VERIFIED** | Physical autonomous avoidance | Dry Run intentionally prevented avoidance-triggered motion during Phase 1-A. |
| **NOT YET VERIFIED** | Live Bedrock inference | Bedrock integration is implemented as the default Strands provider, but live inference verification is pending AWS account/payment activation. |

## Who It Is For

- People experimenting with small home robots that should fail safely.
- Makers and robotics learners who want a clear edge-versus-agent architecture.
- Future home-assistance scenarios where a robot should escalate exceptional conditions instead of requiring continuous monitoring.

GuardianPaw is a prototype. It is not a certified medical, security, or life-safety system.

## Why It Matters

Immediate motion safety should not depend on a network request or a probabilistic model response. GuardianPaw keeps stopping, obstacle response, and servo/gait safety on the ESP32, while the AI layer interprets robot telemetry, explains risk, and decides whether a person should be involved. This makes both the robot behavior and the agent's authority easier to inspect.

## Safety Architecture

The ESP32 local controller owns:

- Immediate stop and fail-safe behavior.
- Local obstacle response.
- Servo control, gait execution, and low-level motion safety.

Guardian Agent owns:

- Interpretation of a structured robot-state snapshot.
- High-level risk explanation.
- Recommendations to continue, wait, pause, or inspect.
- Human escalation when telemetry is unsafe or unavailable.

The language model cannot override deterministic safety constraints. Safety rules are evaluated before model reasoning and enforced again on the structured model response. Guardian Agent does not issue servo angles and does not replace the ESP32 real-time controller.

## How We Use Strands Agents

This is not a chatbot relabeled as a robot controller. The implementation uses:

- A real `strands.Agent` instance.
- Strands' `BedrockModel` as the preferred/default provider, using `global.anthropic.claude-sonnet-4-6` unless explicitly overridden.
- Strands' official `OllamaModel` as an explicit local fallback, with host and model selected through environment variables.
- A custom `@tool` named `evaluate_safety_policy` that returns authoritative, structured safety constraints for the current `RobotState`.
- A Pydantic structured-output model for stable operational decisions.
- Tool-assisted safety evaluation before high-level interpretation.
- Deterministic post-enforcement so the model cannot relax risk level, human escalation, patrol permission, or the required safe action.

Guardian Agent reasons over robot telemetry and returns structured operational decisions while safety-critical constraints remain deterministic. Switching providers does not change the policy/tool/output flow and is never automatic. Live Strands inference is verified locally with Ollama and `llama3.1`; live Amazon Bedrock inference remains pending AWS account/payment activation. The policy-only demo still explicitly states that it performs no model inference.

## Demo Scenarios

| Scenario | Simulated input | Expected result |
|---|---|---|
| 1. Normal Patrol | Valid 800 mm distance and `CLEAR` | Low risk; continue patrol; no human required. |
| 2. Obstacle Detected | Valid 180 mm distance, `OBSTACLE_DETECTED`, local safety engaged | Wait for the ESP32 controller; do not compete with local avoidance. |
| 3. Recovery | Valid 600 mm distance and `RECOVERING` | Observe recovery; resume only after the ESP32 returns to `CLEAR`. |
| 4. Sensor Fault | Invalid distance and `SENSOR_FAULT` | High risk; deny autonomous patrol and require a human. |

## Run the Offline Demo

Python 3.10 or newer is recommended.

```text
cd guardian-agent
python -m venv .venv
python -m pip install -r requirements.txt
python demo.py --policy-only
```

`--policy-only` is a transparent offline/debug path: it prints `TELEMETRY SOURCE: SIMULATED` and `NO MODEL INFERENCE`. Judges do not need a physical quadruped or AWS credentials to run it. See [testing instructions](docs/TESTING.md) for platform-specific setup, tests, and the credential-dependent Strands path.

## Run a Real Strands Provider

Amazon Bedrock is preferred and remains the default. It requires valid AWS credentials, region/model access, and completed account activation:

```text
python demo.py
```

Ollama is an explicit local fallback so judges and developers can run the real Strands Agent without AWS credentials. After installing Ollama and pulling a tool-capable model, use Windows PowerShell:

```text
$env:GUARDIAN_MODEL_PROVIDER="ollama"
$env:OLLAMA_MODEL="llama3.1"
python demo.py
```

There is no silent fallback between providers. See the [Guardian Agent guide](guardian-agent/README.md) for installation and macOS/Linux commands. This exact local provider path completed all four simulated-telemetry scenarios using a real Strands Agent, custom tool invocation, Pydantic structured output, and deterministic post-enforcement.

Ollama emitted a non-fatal warning that forced `ToolChoice` is unsupported. GuardianPaw explicitly invokes `evaluate_safety_policy` through the registered Strands tool before model reasoning, so the current safety-tool path still completed successfully.

## Repository Guide

| Path | Purpose |
|---|---|
| `quad-arduino-wifi/` | ESP32 firmware, Web control, Phase 1-A sensor simulation, and local avoidance. |
| `guardian-agent/` | Strands-based high-level agent, telemetry models, safety policy, CLI demo, and offline tests. |
| `docs/SUBMISSION_ARCHITECTURE.md` | Hackathon-facing architecture diagram and trust boundary. |
| `docs/DEVPOST_SUBMISSION.md` | Draft Devpost submission copy. |
| `docs/DEMO_VIDEO_SCRIPT.md` | 4:30 demo-video plan with explicit simulation disclosures. |
| `docs/PRIOR_WORK.md` | Pre-existing work, third-party code, and hackathon additions. |
| `docs/SUBMISSION_CHECKLIST.md` | Technical and publishing readiness checklist. |
| `THIRD_PARTY_NOTICES.md` | Preserved upstream copyright, license, and provenance notices. |

## Current Limitations and Next Steps

- No live ESP32-to-Agent telemetry transport is implemented; the CLI uses a simulated timeline.
- Physical VL53L1X ranging, expansion-board VCC measurement, and D21/D22 I2C wiring remain unverified.
- Connecting all servos previously produced an ESP32 brownout reset; power-system investigation is deferred and Brownout protection remains enabled.
- Physical autonomous avoidance remains a supervised Phase 1-C milestone.
- Battery telemetry, MPU6050, vision, AgentCore deployment, database, Web UI, and multi-agent operation are not included.
- Live Bedrock inference will be tested only after AWS account/payment activation and model access are available.
- The verified local fallback requires a running Ollama service and a pulled `llama3.1` model. Ollama's forced-`ToolChoice` warning remains disclosed even though GuardianPaw's explicit safety-tool path succeeds.

## License and Attribution

GuardianPaw additions are provided under the root [MIT License](LICENSE). The pre-existing firmware baseline under `quad-arduino-wifi/` retains its own MIT license and copyright notice; the root license does not replace third-party notices. See [Third-Party Notices](THIRD_PARTY_NOTICES.md) and [Prior Work and Third-Party Disclosure](docs/PRIOR_WORK.md) for scope, upstream attribution, and items that still need owner confirmation.

## Project Documentation

- [Testing](docs/TESTING.md)
- [Submission architecture](docs/SUBMISSION_ARCHITECTURE.md)
- [Hardware notes](docs/HARDWARE.md)
- [Development roadmap](docs/ROADMAP.md)
- [Firmware architecture](docs/ARCHITECTURE.md)
- [Prior work](docs/PRIOR_WORK.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)
- [Submission checklist](docs/SUBMISSION_CHECKLIST.md)
