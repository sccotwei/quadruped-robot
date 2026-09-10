---
name: quadruped-robot
description: Use for this repository's ESP32 firmware, sensor integration, motion features, hardware debugging, attitude control, and Raspberry Pi coordination. Route only the context needed for the task.
---

# Quadruped Robot Workflow

Always follow the root `AGENTS.md`; it and the existing project docs are the sources of truth.

## Classify and route

Check `git status`, identify the task type and Phase, then read only matching context:

- Project overview, setup, or usage: `README.md`
- GPIO, I2C, sensors, servos, power, wiring, Raspberry Pi hardware, or physical hardware: `docs/HARDWARE.md`
- New features, Phase work, next steps, or planning: `docs/ROADMAP.md`
- Module boundaries, architecture, ESP32/Raspberry Pi coordination, communication, or broad design: `docs/ARCHITECTURE.md`
- Bugs, anomalies, failed physical tests, debugging, or regressions: `docs/DEBUG_LOG.md`

Do not read documents that the task does not require.

## Scope source reads

Search for relevant filenames, classes, functions, or symbols first. Read the smallest likely source ranges and expand only when evidence is insufficient; do not scan the repository merely to understand everything.

## Implement

1. Define the requested scope, Phase, acceptance evidence, and allowed files.
2. Inspect only the affected boundary and dependencies.
3. Apply the smallest reversible diff under the root `AGENTS.md` constraints; keep new sensor work separated from the existing motion layer.
4. Update project docs only when the task changes their source-of-truth facts.

## Validate

Use only the levels relevant and available: static checks → build/compile → software verification → physical robot test.

If Codex cannot observe the robot, never claim physical success. State `PHYSICAL TEST REQUIRED` and give the minimum safe test steps.

## Git workflow

For feature work, default to: GitHub Issue → feature branch → implementation → build → physical test → commit → push → Pull Request.

Do not automatically commit or push, and do not modify `main` then immediately push. Commit, push, or other external mutations require explicit user authorization. Small documentation-only changes may follow the user's explicit workflow.
