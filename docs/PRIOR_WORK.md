# Prior Work and Third-Party Disclosure

This document separates the pre-existing robot baseline and third-party dependencies from the work added for GuardianPaw. It is an engineering provenance record, not legal advice.

## Pre-existing / Third-party Baseline

| Item | Provenance and license treatment | GuardianPaw use |
|---|---|---|
| Physical quadruped hardware | The assembled robot existed before the GuardianPaw Phase 1 work. Its manufacturer, mechanical-design source, and any design-file license are **NEEDS OWNER CONFIRMATION**. | Physical locomotion platform and ESP32 test target. |
| Arduino Wi-Fi firmware baseline | `quad-arduino-wifi/` corresponds to the public [AniPython/quad-arduino-wifi](https://github.com/AniPython/quad-arduino-wifi) project. The upstream repository identifies an MIT license, and this repository preserves `quad-arduino-wifi/LICENSE` with `Copyright (c) 2025 liang yi`. | Phase 0 locomotion, Web/HTTP control, MiniKame motion routines, oscillator code, UI, and wiring image. |
| MiniKame / Octosnake lineage before AniPython | Names and oscillator-based gait concepts indicate earlier MiniKame lineage, but the exact source chain and authorship before the AniPython repository are not documented in the local files. **NEEDS OWNER CONFIRMATION.** | Retained as the working motion baseline; not claimed as GuardianPaw-original work. |
| Arduino and ESP32 libraries | Arduino framework, ESP32 Arduino Core, ESP32Servo, ArduinoJson, Wire, Adafruit VL53L1X, and Adafruit BusIO are external dependencies and are not vendored here. | Firmware build and hardware abstraction dependencies; each remains governed by its upstream license. |
| Agent libraries | Strands Agents SDK and Pydantic are external Python dependencies and are not vendored here. | Agent orchestration, custom tool integration, and structured output validation; each remains governed by its upstream license. |

## Built for GuardianPaw During the Hackathon

The GuardianPaw work is separated from the retained locomotion baseline in the repository history and architecture:

- VL53L1X distance-sensor abstraction with real and simulated modes.
- Transparent simulated ToF telemetry pipeline.
- Obstacle-avoidance state machine with threshold hysteresis.
- Invalid-measurement and initialization fail-safe behavior.
- Dry Run actuator isolation for the avoidance controller.
- Boot diagnostics and non-blocking state timing added during Phase 1-A stabilization.
- `RobotState` and structured `AgentDecision` contracts.
- Deterministic safety policy and deterministic post-enforcement.
- Real Strands `Agent` setup, Bedrock provider path, and custom `@tool` integration.
- Four-scenario CLI demo and offline safety-policy tests.
- GuardianPaw submission architecture, testing guide, Devpost draft, video script, and disclosure documentation.

These additions do not replace or claim authorship of the pre-existing gait algorithms, servo configuration, Web controller baseline, physical chassis, or upstream dependencies.

## License Scope

- The root `LICENSE` applies the MIT License to GuardianPaw-owned original portions and submission documentation, copyright 2026 GuardianPaw contributors.
- The pre-existing `quad-arduino-wifi/` baseline retains its own MIT license and copyright notice. That notice must remain with copies or substantial portions of the baseline.
- Third-party packages are referenced as dependencies, not relicensed by this repository.
- No license claim is made here over the physical robot design, seller materials, or any external media not owned by GuardianPaw contributors.

## Owner Confirmations Required Before Final Submission

- **NEEDS OWNER CONFIRMATION:** identify the robot hardware manufacturer/seller and whether any mechanical or wiring design files shown publicly require attribution.
- **NEEDS OWNER CONFIRMATION:** confirm the MiniKame/Octosnake source chain before adding any attribution more specific than the directly verified AniPython repository.
- **NEEDS OWNER CONFIRMATION:** confirm permission for every photo, diagram, logo, soundtrack, and video clip used in the final Devpost or demo video. Do not reuse seller media without permission.
- **NEEDS OWNER CONFIRMATION:** confirm the final contributor names, project-eligibility dates, and copyright ownership for the hackathon submission.

## Evidence Used for This Record

- The repository's initial baseline commit adds `quad-arduino-wifi/` before the GuardianPaw Phase 1 and Agent commits.
- The local firmware license is MIT with the 2025 `liang yi` copyright notice.
- The public AniPython repository exposes the same firmware filenames and identifies the project as MIT-licensed.
- GuardianPaw Phase 1-A and Guardian Agent MVP are separated in later checkpoint commits.
