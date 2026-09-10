# AGENTS.md

本文件适用于整个 `quadruped-robot` 仓库。

## 每次任务

1. 阅读本文件。
2. 检查 `git status`，保留用户已有变更。
3. 根据用户任务判断当前 Phase、允许修改范围和必要上下文。

## 按需加载文档

只在任务命中对应范围时读取；不需要的文档不要读取。

- `README.md`：项目概览、安装、使用说明或文档维护。
- `docs/HARDWARE.md`：GPIO、I2C、传感器、舵机、供电、接线、Raspberry Pi 或实体硬件。
- `docs/ARCHITECTURE.md`：模块边界、软件架构、ESP32/Raspberry Pi 协同、通信或大范围重构。
- `docs/ROADMAP.md`：新功能、Phase 状态、下一阶段或项目规划。
- `docs/DEBUG_LOG.md`：bug、硬件异常、实体测试、调试或回归问题。

## Baseline 安全约束

- `quad-arduino-wifi/minikame.cpp` 中可工作的基础行走与舵机控制是 Phase 0 baseline。
- 除非用户明确要求，不得修改现有运动行为、舵机参数、相位、幅度、偏移、周期、回中姿态或 GPIO。
- 不猜测 GPIO、舵机型号、方向、机械结构、接线、供电、总线或其他硬件信息。
- 未经代码、硬件记录或用户确认的信息使用 `UNKNOWN` 或 `TODO`。
- 不进行无关重构，不提前开始未明确授权的 Phase。
- 不提交或泄露 Wi-Fi 密码、Token 或其他本地凭据。

## 实施与验证

- ESP32 继续负责实时运动控制；新传感器功能与现有运动层保持清晰边界。
- 优先采用小范围、可验证、可回退的变更。
- 修改前明确 baseline 行为和验证条件，修改后只执行相关验证。
- 无法进行硬件测试时标记为 `UNKNOWN` 或 `TODO`，不得声称已经验证。
- 仅在任务产生相关变化时更新对应文档或调试记录。
