# Testing GuardianPaw Without a Robot

Judges do not need a physical quadruped robot to run the deterministic policy tests or the policy-only demonstration. The current CLI telemetry is simulated and labels itself accordingly.

## Requirements

- Python 3.10 or newer.
- A virtual environment is recommended.

From the repository root:

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

## Offline Safety-policy Tests

These tests do not access AWS or a model endpoint:

```text
python -m unittest discover -s tests -v
```

Coverage includes normal patrol, active obstacle handling, sensor fault, telemetry disconnection, and rejection of a model candidate that attempts to relax a hard rule.

## Policy-only Demo

```text
python demo.py --policy-only
```

Expected disclosure headers:

```text
TELEMETRY SOURCE: SIMULATED
DECISION PIPELINE: DETERMINISTIC POLICY ONLY (NO MODEL INFERENCE)
```

The command runs four simulated scenarios: normal patrol, obstacle detected, recovery, and sensor fault. It is a deterministic fallback/debug path, not proof of Strands model inference.

## Strands / Amazon Bedrock Path

The normal path creates and invokes the real Strands Agent:

```text
python demo.py
```

This path requires AWS authentication, an AWS region, network access, and permission to invoke the selected Amazon Bedrock model. Configure credentials through the standard AWS credential chain; never put credentials in this repository. `GUARDIAN_BEDROCK_MODEL_ID` may select a model without hard-coding an account.

At this submission-pack checkpoint, Bedrock integration is implemented as the default Strands provider, but live inference verification is pending AWS account/payment activation. A credentials, access, or provider error must be reported as a blocker rather than presented as successful model output.

## Hardware Evidence Boundary

The offline commands do not verify physical hardware. Phase 1-A has separately been run on a real ESP32 with simulated distance input and avoidance Dry Run enabled. Real VL53L1X ranging, physical I2C wiring, power stability with all servos, and physical autonomous avoidance require supervised hardware tests described in `ROADMAP.md` and `HARDWARE.md`.
