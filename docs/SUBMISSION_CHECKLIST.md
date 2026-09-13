# GuardianPaw Submission Checklist

This checklist reflects repository readiness at the Submission Pack checkpoint. Remote publishing, account state, and media rights must be confirmed by the project owner.

## Required

- [ ] Public GitHub repository
- [x] MIT/Apache license
- [ ] License visible in GitHub About
- [x] Root README
- [x] Architecture diagram
- [x] Devpost text description
- [ ] Demo video no longer than 5 minutes
- [ ] Video public on YouTube or Vimeo
- [ ] AWS Builder ID
- [ ] Everyday Agents track selected
- [x] Testing instructions
- [x] Prior-work disclosure

## Technical

- [x] Real Strands Agent usage visible in source
- [x] Custom `@tool` visible in source
- [x] Deterministic safety-policy tests
- [x] `demo.py --policy-only` works offline
- [x] Bedrock live inference limitation disclosed in every current submission surface; live inference itself remains unverified

## Hardware

- [ ] Locomotion footage recorded and rights confirmed
- [ ] ESP32 Phase 1-A Serial footage recorded and rights confirmed
- [x] No claim of hardware ToF verification

## Optional

- [ ] Live demo
- [ ] AgentCore deployment
- [ ] `builder.aws` post

## Final Accuracy Pass

- [ ] Replace the Bedrock limitation only after a real inference succeeds and its output is captured.
- [ ] Keep `TELEMETRY SOURCE: SIMULATED` visible while the demo uses simulated ToF values.
- [ ] Verify no AWS account ID, credential, token, Wi-Fi secret, or local absolute path is committed.
- [ ] Verify all external media permissions and the owner confirmations in `PRIOR_WORK.md`.
- [ ] Confirm `quad-arduino-wifi/` behavior is unchanged from the verified Phase 1-A checkpoint.

## Suggested GitHub About

**Description:** Embodied home-safety agent combining an ESP32 quadruped, deterministic edge safety, and Strands-based high-level reasoning.

**Topics:** `strands-agents`, `aws`, `amazon-bedrock`, `esp32`, `robotics`, `quadruped`, `ai-agent`

**Website:** leave empty until a project page exists.

These are suggestions only; this repository task does not modify the GitHub remote.
