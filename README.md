# quadruped-robot

基于 ESP32 的四足机器人项目。当前可工作的基础行走代码被定义为 **Phase 0 baseline**，后续功能必须在保持现有运动行为、舵机参数和 GPIO 配置不变的前提下逐步扩展。

## 当前状态

- 当前阶段：Phase 0 基础行走 baseline
- 主控：ESP32
- 技术栈：Arduino Framework / C++
- 控制方式：ESP32 WebServer 接收网页控制命令
- 当前能力：基础前进、后退、左右转及已有动作
- 当前运动逻辑位置：`quad-arduino-wifi/minikame.cpp`
- 当前程序入口：`quad-arduino-wifi/quad-arduino-wifi.ino`

## Baseline 约束

- 未经明确授权，不修改现有运动行为。
- 未经明确授权，不调整舵机参数、动作相位、幅度、偏移或周期。
- 不猜测或擅自更改 GPIO、舵机型号及接线。
- 新硬件功能按 `docs/ROADMAP.md` 分阶段实施。
- 当前任务范围不包含 VL53L1X 开发。

## 目录结构

```text
quadruped-robot/
├── AGENTS.md
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEBUG_LOG.md
│   ├── HARDWARE.md
│   └── ROADMAP.md
└── quad-arduino-wifi/
    ├── quad-arduino-wifi.ino
    ├── minikame.cpp
    ├── minikame.h
    ├── Octosnake.cpp
    ├── Octosnake.h
    ├── WiFiSetup.h
    ├── Config.example.h
    ├── Config.h
    ├── index.html
    ├── convert_html.py
    └── images/
```

## 构建信息

- Arduino IDE 或 Arduino CLI 版本：UNKNOWN
- ESP32 Arduino Core 版本：UNKNOWN
- ESP32 具体开发板型号及 FQBN：UNKNOWN
- `ESP32Servo` 版本：UNKNOWN
- `ArduinoJson` 版本：UNKNOWN
- 可复现构建与上传命令：TODO

## 首次编译前的本地配置

将示例配置复制为本地配置：

```text
quad-arduino-wifi/Config.example.h
->
quad-arduino-wifi/Config.h
```

然后仅在本地填写自己的 Wi-Fi 配置。`Config.h` 包含本机凭据，已被 Git 忽略，不应提交到 Git；`Config.example.h` 只包含可公开的占位符和编译所需结构。

工程管理 TODO：`quad-arduino-wifi/.gitignore` 中现有的 `lib/` 规则可能影响未来加入的本地 Arduino 库；当前没有 `lib/` 目录，暂不修改该规则，待实际引入本地库时复查。

## 文档

- [硬件信息](docs/HARDWARE.md)
- [程序架构](docs/ARCHITECTURE.md)
- [开发路线](docs/ROADMAP.md)
- [调试记录](docs/DEBUG_LOG.md)
