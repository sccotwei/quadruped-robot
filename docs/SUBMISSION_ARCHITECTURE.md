# GuardianPaw Submission Architecture

GuardianPaw separates time-critical robot safety from high-level interpretation. Solid arrows show the current data and decision design. The dotted model path is implemented through Strands' default Amazon Bedrock provider, but live Bedrock inference is pending AWS account/payment activation and has not been verified.

```mermaid
flowchart TD
    subgraph EDGE[Physical / Edge Layer]
        ENV[Home environment]
        TOF["VL53L1X interface<br/>CURRENTLY SIMULATED ToF INPUT"]
        ESP[ESP32 local controller]
        GAIT[Gait / servo control]
        AVOID[Local obstacle avoidance]
        FAIL[Fail-safe controller]

        ENV --> TOF --> ESP
        ESP --> GAIT
        ESP --> AVOID
        ESP --> FAIL
    end

    ESP -->|Telemetry snapshot| STATE[RobotState]

    subgraph GUARDIAN[Guardian Decision Layer]
        STATE --> POLICY[Deterministic Safety Policy]
        POLICY --> AGENT[Strands Agent]
        AGENT -->|"Invoke custom @tool"| TOOL[evaluate_safety_policy]
        TOOL -->|Authoritative safety assessment| AGENT
        AGENT --> DECISION[Structured high-level recommendation]
        DECISION --> HUMAN{Human intervention required?}
        HUMAN -->|Yes| ESCALATE[Human escalation]
        HUMAN -->|No| GUIDANCE[Continue / wait / pause guidance]
    end

    subgraph MODEL[Model Provider Path]
        AGENT -.->|Implemented; live inference pending| BEDROCK[Amazon Bedrock]
        BEDROCK -.-> CLAUDE[Claude model]
    end
```

The editable Mermaid source is also available in [`architecture.mmd`](architecture.mmd).

## Responsibility Boundary

| Layer | Owns | Must not delegate |
|---|---|---|
| ESP32 local controller | Gait, servo output, immediate stop, local obstacle response, and fail-safe state | Immediate physical safety |
| Deterministic policy | Hard risk classification, patrol permission, and required human escalation | Safety constraints that a model could weaken |
| Strands Agent | Telemetry interpretation, explanation, and high-level recommendation | Servo commands or overrides of local safety |
| Human | Inspection and recovery when telemetry or hardware cannot be trusted | N/A |

The model can add context and explanation, but deterministic post-enforcement fixes the final risk level, patrol permission, escalation flag, and required safe action.

## Verification Boundary

- **Verified on physical ESP32:** Phase 1-A simulated distances, complete avoidance state transitions, and Dry Run isolation of avoidance-triggered actuators.
- **Verified offline:** deterministic policy tests and the four-scenario policy-only CLI demo.
- **Implemented but not live-verified:** Strands-to-Bedrock inference.
- **Not verified:** physical VL53L1X ranging, D21/D22 I2C wiring, autonomous physical avoidance, MPU6050, and vision.
