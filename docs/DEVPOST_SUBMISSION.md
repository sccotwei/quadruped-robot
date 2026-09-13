# GuardianPaw Devpost Submission Draft

## Project Name

GuardianPaw

## Tagline

An embodied home-safety agent that keeps immediate robot safety at the edge and escalates only when a human is needed.

## Track Recommendation

Everyday Agents

## Why This Track

GuardianPaw is designed around an everyday human need: a small home robot should handle ordinary local hazards without demanding constant supervision, while clearly asking for help when its telemetry cannot be trusted. It demonstrates an agent that interprets an embodied system's state and turns it into safe, understandable recommendations rather than acting as a general-purpose chatbot.

## What It Does

GuardianPaw combines a physical ESP32 quadruped robot with two deliberately separate decision layers. On the robot, a deterministic controller owns gait, servos, immediate stopping, obstacle response, and fail-safe behavior. Above that boundary, Guardian Agent consumes a structured `RobotState`, explains the current situation, classifies risk, recommends a high-level action, decides whether autonomous patrol may continue, and indicates when a person must intervene.

The Phase 1-A firmware demo runs on a real ESP32. It uses a transparent simulated ToF distance sequence to exercise the full avoidance cycle: clear path, obstacle detection, backing up, turning, recovery, and return to clear. Dry Run mode prevents the avoidance controller from driving actuators while preserving state timing and Serial action logs.

The local CLI demonstrates four states: normal patrol, an obstacle handled by local safety, recovery, and a sensor fault. A deterministic policy establishes non-negotiable constraints before AI reasoning. A real Strands Agent is configured with a custom safety-evaluation tool and structured output; the same policy is enforced again afterward so a model cannot relax it.

The current Guardian Agent timeline uses simulated robot telemetry, but the model path is real: live Strands inference was verified locally with Ollama and `llama3.1` across all four scenarios. Bedrock integration remains the preferred/default provider, but live Amazon Bedrock inference verification is pending AWS account/payment activation.

## The Problem

Most small robot demos assume a person is always watching or put perception, movement, and AI reasoning into one opaque loop. Neither approach is suitable for an everyday robot. Immediate hazards require fast, predictable responses even when connectivity or a model is unavailable, while unusual failures need a clear explanation and human escalation. GuardianPaw addresses that gap by giving the ESP32 authority over physical safety and giving the agent a narrower, auditable role: interpret telemetry, explain risk, and recommend what should happen next without competing with the controller already protecting the robot.

## How We Built It

We preserved the working MiniKame-based locomotion and Web-control baseline instead of rewriting the gait layer. Phase 1-A added a small VL53L1X abstraction that represents initialization, measurement validity, timeout, and distance in millimeters. A compile-time simulation mode supplies a non-blocking sequence of distances, and centralized enter/exit thresholds provide hysteresis around the obstacle boundary.

An ESP32 avoidance state machine coordinates `CLEAR`, `OBSTACLE_DETECTED`, `BACKING_UP`, `TURNING`, `RECOVERING`, and `SENSOR_FAULT`. Timing uses `millis()` so sensing and HTTP handling retain room to run. A second compile-time Dry Run boundary intercepts only actions requested by the avoidance controller. This let us validate the full state cycle on physical ESP32 hardware without allowing autonomous servo motion. Invalid telemetry fails safe, and existing user Web control and locomotion code remain separate.

For the high-level layer, we created a Python 3.10+ package around a typed `RobotState` and stable `AgentDecision`. Deterministic policy evaluates connection, distance validity, local-safety engagement, and avoidance state. The policy-only path runs completely offline for repeatable judging. The Strands path constructs a real `strands.Agent`, registers the read-only `evaluate_safety_policy` custom tool, requests a Pydantic structured response, and then clamps the output to the deterministic assessment.

Tests cover normal patrol, active avoidance, sensor fault, disconnection, and an intentionally unsafe model candidate. Documentation records the edge/agent trust boundary, simulation status, hardware limitations, and prior work.

## How We Use Strands Agents

Guardian Agent uses an actual `strands.Agent`, not a renamed rules engine. Amazon Bedrock remains the preferred/default provider, and Ollama is an explicit local fallback rather than a silent replacement. The agent receives serialized robot telemetry plus an authoritative safety assessment, and it is instructed to interpret the situation without producing servo angles or competing motion commands.

The custom `@tool`, `evaluate_safety_policy`, validates a serialized `RobotState` and returns risk, patrol permission, escalation, required action, and reason. The agent's response is constrained through a Pydantic output model containing the situation, risk level, recommendation, human-escalation flag, reason, and autonomous-patrol permission.

Safety does not depend on prompt compliance. The same deterministic result is enforced after the Strands response, so model text cannot lower risk, allow patrol, remove a required human escalation, or replace the mandated safe action. Live local Strands inference with Ollama and `llama3.1` completed all four scenarios with structured output and no validation errors; Bedrock live inference remains pending account/payment activation. The offline policy demo continues to say explicitly that it performs no model inference.

## Challenges

The hardest challenge was keeping a useful agent architecture without giving a probabilistic model unsafe authority. We had to define exactly what belongs on the ESP32, what the deterministic policy owns, and what the model may explain. Hardware availability created a second constraint: the new VL53L1X was not available, so every ToF claim had to remain visibly simulated. A brownout observed with all servos connected also reinforced that software progress must not be confused with power-system readiness. Bedrock account/payment activation delayed cloud verification, so we retained an honest policy-only path and added an explicit Ollama fallback for real local Strands inference.

## Accomplishments

We preserved the known-good locomotion baseline while adding a separable distance interface, fail-safe obstacle state machine, hysteresis, non-blocking simulated telemetry, and actuator Dry Run protection. On a real ESP32, we observed the complete avoidance cycle and confirmed that Dry Run prevented avoidance-triggered servo actions. We also built the Guardian Agent MVP with a real Strands Agent, a meaningful custom tool, typed telemetry, structured decisions, deterministic pre-checks, and post-enforcement. Ten offline tests, the four-scenario policy-only demo, and a successful four-scenario live Strands run with Ollama provide repeatable evidence without claiming physical ToF or Bedrock verification.

## What We Learned

An embodied agent becomes easier to trust when its authority is intentionally limited. The ESP32 should not wait for cloud reasoning before responding to an obstacle, and a polished explanation should never be allowed to weaken a stop condition. Simulation is valuable when it is explicit: it let us test every state transition and failure path before connecting a sensor or enabling motion. We also learned that hardware readiness includes power integrity, wiring, and braking distance—not just successful compilation—and that those unknowns belong in the architecture and demo narrative rather than being hidden.

## What's Next

Phase 1-B will measure the expansion-board VCC, verify the proposed D21/D22 I2C path, connect the VL53L1X, and validate real ranging while actuator Dry Run remains enabled. After threshold and braking-distance calibration, Phase 1-C will test physical avoidance under supervision. In parallel, once AWS account/payment activation and model access are available, we will capture a real Bedrock inference run and update the disclosure. A later integration can define a read-only ESP32 telemetry transport into the existing `RobotState` contract. MPU6050, vision, and broader home behaviors remain future phases rather than claims of this MVP.

## Current Limitations

- The hackathon CLI consumes simulated telemetry; it is not connected live to the ESP32.
- ToF values are simulated. A physical VL53L1X, its VCC, and D21/D22 I2C communication are not verified.
- Physical autonomous avoidance has not been tested; Phase 1-A used actuator Dry Run.
- Live Amazon Bedrock inference has not been verified because AWS account/payment activation is pending.
- Live local Strands inference is verified with Ollama and `llama3.1`. Ollama emitted a non-fatal warning that forced `ToolChoice` is unsupported; GuardianPaw's explicit registered-tool invocation still completed successfully.
- A servo-connected brownout risk remains under hardware investigation; Brownout protection is not disabled.
- Battery telemetry is unavailable, and MPU6050, vision, AgentCore, Web UI, database, and multi-agent features are not implemented.
- GuardianPaw is a prototype and is not a certified medical, security, or life-safety system.
