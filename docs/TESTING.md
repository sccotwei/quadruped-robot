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

## Real Strands Provider Paths

Both provider paths create the same real Strands Agent, register the same `evaluate_safety_policy` custom tool, request the same Pydantic structured output, and apply the same deterministic post-enforcement. Provider selection is explicit and never falls back silently.

### Amazon Bedrock — preferred and default

The default path requires AWS authentication, an AWS region, network access, and permission to invoke `global.anthropic.claude-sonnet-4-6` unless `GUARDIAN_BEDROCK_MODEL_ID` overrides it:

```text
python demo.py
```

Configure credentials through the standard AWS credential chain; never put credentials in this repository.

At this submission-pack checkpoint, Bedrock integration is implemented as the default Strands provider, but live inference verification is pending AWS account/payment activation. A credentials, access, or provider error must be reported as a blocker rather than presented as successful model output.

### Ollama — explicit local fallback

The official Strands Ollama extra is declared in `requirements.txt`. To add it to an existing environment:

```text
python -m pip install 'strands-agents[ollama]>=1.55,<2'
```

Install [Ollama](https://ollama.com/download), pull `llama3.1`, and ensure the local service is running. Then run the verified Windows PowerShell path:

```text
ollama pull llama3.1
$env:GUARDIAN_MODEL_PROVIDER="ollama"
$env:OLLAMA_MODEL="llama3.1"
python demo.py
```

`OLLAMA_HOST` defaults to `http://localhost:11434`; `OLLAMA_MODEL` has no code default and must identify a model that is actually installed. No AWS credentials are required for this explicit local fallback.

This path was live-verified on Windows with Ollama 0.34.0 and `llama3.1:latest`. A real Strands Agent completed normal patrol, obstacle detected, recovery, and sensor fault with exit code 0 in approximately 28.85 seconds. The registered custom tool executed successfully, Pydantic structured output produced no validation errors, and deterministic post-enforcement preserved the required safety results.

The provider emitted a non-fatal warning that forced `ToolChoice` is unsupported. GuardianPaw explicitly invokes `evaluate_safety_policy` through the registered Strands tool before inference, so its current safety-tool path does not rely on that provider capability and completed successfully.

## Hardware Evidence Boundary

The offline commands do not verify physical hardware. Phase 1-A has separately been run on a real ESP32 with simulated distance input and avoidance Dry Run enabled. Real VL53L1X ranging, physical I2C wiring, power stability with all servos, and physical autonomous avoidance require supervised hardware tests described in `ROADMAP.md` and `HARDWARE.md`.
