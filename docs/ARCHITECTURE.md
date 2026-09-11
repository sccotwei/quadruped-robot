# Architecture

## 当前架构（Phase 1 软件集成）

```text
浏览器控制页面
       |
       | HTTP POST /control
       v
ESP32 WebServer
       |
       v
processCommand()
       |                         距离传感器层
       |                              |
       |                              v
       +----> 前进安全门控 <---- 避障状态机
       |                              |
       +------------------------------+
                                      |
                                      v
                              MiniKame 动作层
                                      |
                                      +--> execute() / moveServos()
                                      |          |
                                      |          v
                                      |      Oscillator
                                      |          |
                                      v          v
                                    setServo() -> ESP32Servo -> 舵机
```

## 程序入口与运行流程

1. `quad-arduino-wifi/quad-arduino-wifi.ino` 中的 `setup()` 初始化 LED、串口、距离传感器、Wi-Fi、HTTP 服务、机器人对象和避障控制器。
2. `robot.init()` 初始化现有舵机控制，随后执行 `robot.home()`。
3. `loop()` 更新距离数据和避障状态机，并调用 `server.handleClient()` 处理控制请求。
4. `/control` 请求由 `handlePost()` 解析，并交给 `processCommand()`。
5. 前进命令先经过避障状态门控，获准后才调用 `MiniKame` 的已有动作函数。
6. 动作层通过插值或振荡器输出舵机目标位置。

## 当前模块

| 模块 | 文件 | 职责 |
|---|---|---|
| Arduino 入口与 Web 控制 | `quad-arduino-wifi.ino` | 初始化、HTTP 路由、命令分发 |
| VL53L1X 距离采集 | `VL53L1XDistanceSensor.h/.cpp` | 真实/模拟数据、初始化和测量状态、限频 Serial 诊断；不调用运动层 |
| 基础避障 | `ObstacleAvoidance.h/.cpp` | 阈值迟滞、故障安全、状态转换与现有动作编排 |
| 机器人运动控制 | `minikame.h/.cpp` | 舵机控制、基础步态和已有动作 |
| 步态振荡器 | `Octosnake.h/.cpp` | 周期、幅度、相位和偏移计算 |
| 网络配置 | `WiFiSetup.h`、本地 `Config.h` | AP/STA 初始化与地址配置 |
| 控制页面 | `index.html` | 浏览器控制界面源文件 |
| 页面转换工具 | `convert_html.py` | 将 HTML 转换为 Arduino 字符串 |

## Baseline 边界

- 当前运动参数及 GPIO 配置保持不变。
- 距离更新和状态等待使用 `millis()`，不新增长 `delay()`。
- 现有 gait 动作调用为同步执行；后退/转向期间不能轮询传感器。是否改造为非阻塞运动架构：TODO，仅在明确授权后评估。
- 当前硬件构建和实机回归测试流程：TODO。

## 规划架构

```text
Raspberry Pi（高级视觉 / 导航 / 行为决策）
                    |
                    | 通信协议：UNKNOWN
                    v
ESP32（状态机 / 传感 / 姿态闭环 / 实时运动控制）
                    |
                    v
                  舵机
```

计划中的传感器输入包括 VL53L1X 距离信息和 MPU6050 姿态信息。具体任务调度、数据接口、频率、GPIO、总线和通信协议均为 `UNKNOWN`，应在对应 Phase 开始前确定。

