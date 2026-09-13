# GuardianPaw Demo Video Script

**Target duration:** 4:30

**Hard limit:** 5:00

**Disclosure rule:** keep `SIMULATED ToF` visible whenever distance telemetry is shown. Local Strands inference with Ollama is verified; Amazon Bedrock must remain labeled as pending unless a separate real Bedrock run is recorded.

## 0:00-0:20 — Problem / Hook

**Visual:** A short close-up of GuardianPaw, then a split screen: the robot on one side and a simple “safe / needs help” decision on the other. Avoid showing unverified sensors as operational.

**Voiceover:** “A home robot should not need a person watching every step. It should handle immediate local hazards by itself, explain what is happening, and ask for help only when the situation cannot be trusted. GuardianPaw explores that boundary with a physical quadruped and a high-level safety agent.”

**On-screen text:** `GuardianPaw — edge safety + high-level agent reasoning`

## 0:20-0:45 — Who It Is For + Why It Matters

**Visual:** Three simple cards: home robot users, makers, future assistance scenarios. Transition to two separate blocks labeled ESP32 and Guardian Agent.

**Voiceover:** “This prototype is for people exploring useful small home robots and for makers learning how to design them responsibly. Instead of mixing gait control, obstacle response, and AI into one opaque loop, GuardianPaw separates deterministic physical safety from language-model interpretation. The fast controller stays on the robot; the agent handles context and escalation.”

**On-screen text:** `Immediate safety stays local` / `The agent cannot override it`

## 0:45-1:15 — Physical GuardianPaw Locomotion

**Visual:** Owner-recorded footage of the known-good physical quadruped walking and responding to existing Web controls. Show the ESP32 and browser control briefly. Use only media owned or cleared by the project owner.

**Voiceover:** “GuardianPaw starts from a real ESP32 quadruped with a working MiniKame-based locomotion baseline and Wi-Fi HTTP control. We preserved the gait algorithms, servo pins, and existing movements. The new safety work sits beside that baseline rather than replacing it, so the same low-level controller remains responsible for the physical robot.”

**On-screen text:** `REAL: quadruped + ESP32 + locomotion + Wi-Fi/HTTP`

## 1:15-1:50 — ESP32 Phase 1-A Serial Demo

**Visual:** Real Serial capture showing `[TOF][SIM]` values and the complete state sequence. Highlight `[AVOID][DRYRUN]` action lines. Include a persistent `SIMULATED ToF` badge.

**Voiceover:** “Phase 1-A runs on the physical ESP32, but the ToF distances are explicitly simulated. The non-blocking sequence approaches an obstacle and exercises every transition: clear, obstacle detected, backing up, turning, recovering, and clear again. Dry Run preserves the timing and action requests while blocking avoidance-triggered servo calls, so this test validates software behavior without autonomous movement.”

**On-screen text:** `REAL ESP32 SOFTWARE` / `SIMULATED ToF` / `DRY RUN: NO AVOIDANCE ACTUATION`

## 1:50-2:40 — Guardian Agent Demo

**Visual:** Terminal running the live local `python demo.py` path with `MODEL PROVIDER: OLLAMA` and `TELEMETRY SOURCE: SIMULATED` both visible. Show the four scenario decisions with risk, patrol permission, and human escalation highlighted. Briefly cut to the real Strands Agent construction and provider selection in source.

**Voiceover:** “The high-level Guardian Agent consumes simulated telemetry as a structured RobotState, but the reasoning path here is real. A Strands Agent uses the local Ollama fallback with llama3.1, invokes the registered safety tool, validates a structured response, and reapplies deterministic constraints. Normal patrol is low risk. For an obstacle, the agent waits for the ESP32. During recovery, patrol remains paused. A sensor fault becomes high risk, denies autonomous patrol, and requires a human. Amazon Bedrock remains the preferred provider, but its live verification is still pending account activation.”

**On-screen text:** `TELEMETRY SOURCE: SIMULATED` / `LIVE STRANDS + OLLAMA / llama3.1` / `Bedrock live verification: pending`

## 2:40-3:20 — Safety Architecture / Strands Tool Flow

**Visual:** Animate the Mermaid diagram from the ESP32 to `RobotState`, deterministic policy, Strands Agent, custom tool, structured decision, and human escalation. Zoom briefly into the `@tool` decorator and Pydantic output model.

**Voiceover:** “Here is the key safety boundary. The ESP32 owns immediate stop, obstacle response, gait, and servos. Robot telemetry becomes a typed state. Deterministic rules first set the minimum risk, whether patrol is allowed, and whether a human is required. A real Strands Agent uses a custom evaluate-safety-policy tool and Pydantic structured output. This complete path is verified locally with Ollama. After reasoning, the hard policy is enforced again, so the model cannot override a sensor fault or an engaged local controller.”

**On-screen text:** `Policy -> Strands Agent <-> custom @tool -> structured decision` / `Deterministic post-enforcement`

## 3:20-3:50 — Sensor Fault / Human Escalation

**Visual:** Replay only Scenario 4. Highlight `distance_valid: false`, `SENSOR_FAULT`, `risk_level: high`, `requires_human: true`, and `allow_autonomous_patrol: false`.

**Voiceover:** “The sensor-fault case shows why this is more than a chatbot. Invalid distance data is a hard safety condition. The policy keeps the robot logically stopped, denies autonomous patrol, and requires a person to inspect the sensor. Natural-language reasoning may explain that decision, but it cannot lower the risk or remove the escalation.”

**On-screen text:** `SENSOR_FAULT -> HIGH RISK -> HUMAN REQUIRED`

## 3:50-4:15 — Current Limitations + Roadmap

**Visual:** Honest roadmap cards: Phase 1-B sensor verification, power investigation, Bedrock verification, Phase 1-C supervised motion. Put a warning icon beside the unmeasured expansion-board VCC and brownout item.

**Voiceover:** “Today, the VL53L1X is not physically verified, D21 and D22 have not been tested as wired I2C, and autonomous physical avoidance has not run. A servo-connected brownout also needs power investigation. Next, we will measure VCC, validate real ranging with Dry Run still on, verify Bedrock inference, calibrate stopping distance, and only then test supervised motion.”

**On-screen text:** `No physical ToF claim` / `No live Bedrock claim yet` / `Safety checks before motion`

## 4:15-4:30 — Closing

**Visual:** Return to GuardianPaw, then finish on the architecture boundary and repository URL placeholder.

**Voiceover:** “GuardianPaw's goal is simple: keep urgent safety deterministic and local, use an agent where interpretation helps, and involve a human when evidence runs out. It is a small robot with a deliberately clear line of responsibility.”

**On-screen text:** `GuardianPaw` / `Local safety. Structured reasoning. Human escalation.`

## Recording Notes

- Planned runtime is exactly **4:30** from the section timestamps.
- Record the Serial monitor at its configured application baud rate; bootloader output may use a different baud rate.
- Do not stage unverified hardware to look operational.
- When recording the verified local model path, show both `MODEL PROVIDER: OLLAMA` and `TELEMETRY SOURCE: SIMULATED`; never label that footage as Bedrock inference.
- If the non-fatal forced-`ToolChoice` warning appears, do not hide it. Explain that GuardianPaw explicitly invokes its registered safety tool and that the current flow completes successfully.
- Confirm ownership or permission for every visual, logo, soundtrack, and clip before publishing.
