# Roadmap

## 阶段规则

- Phase 0 是当前可工作的基础行走 baseline。
- 后续阶段必须逐阶段推进，不得破坏已经通过验证的低层能力。
- 每一阶段开始前确认硬件、接口、GPIO、供电和验收条件；未知项标记为 `UNKNOWN` 或 `TODO`。
- 时间计划：UNKNOWN。

## Phase 0：基础行走 baseline

状态：CURRENT / BASELINE

- 保留当前 ESP32 Arduino 工程。
- 保留当前前进、后退、左右转及已有动作。
- 保留当前舵机参数、GPIO 配置和运动算法。
- 建立 Git 与工程文档结构。
- 实机 baseline 验收步骤：TODO。

## Phase 1：VL53L1X 距离检测与基础前向避障

状态：PHASE 1-A SOFTWARE SIMULATION VERIFIED ON REAL ESP32 / PHASE 1-B PENDING

- 已增加独立 VL53L1X 软件接口，表达初始化、有效数据、无效数据、timeout 和毫米距离。
- 已增加默认启用的 5 Hz 模拟距离序列，以及带 `[TOF][SIM]` 标记的限频 Serial 输出。
- 已增加 `CLEAR -> OBSTACLE_DETECTED -> BACKING_UP -> TURNING -> RECOVERING` 避障状态机、传感器故障安全状态和进入/退出迟滞。
- 已增加默认启用的避障执行器 Dry Run；它保留完整状态计时和动作日志，但不执行避障模块请求的 `home()`、`backward()` 或 `turnR()`。
- Phase 1-A 已在真实 ESP32 上以 `DISTANCE_SENSOR_SIMULATION=1`、`OBSTACLE_AVOIDANCE_DRY_RUN=1` 完成编译、上传和运行验证。
- 已实测确认模拟距离稳定循环，完整经历 `CLEAR -> OBSTACLE_DETECTED -> BACKING_UP -> TURNING -> RECOVERING -> CLEAR`，且 Dry Run 下没有避障模块引发的真实舵机动作。
- 当前初始阈值为进入 250 mm、退出 350 mm，仅用于首轮软件测试，必须根据实机传感器与制动距离校准。
- 已复用现有 `home()`、`backward()`、`turnR()` 动作接口，未修改 Phase 0 gait、舵机参数或 GPIO。
- 已对 Web 前进命令增加安全门控：传感器无效或避障未回到 `CLEAR` 时禁止向前。
- Phase 1-B 真实 VL53L1X、expansion-board VCC 电压测量、GPIO21 / GPIO22 物理 I2C 验证：TODO / PHYSICAL TEST REQUIRED。
- 舵机连接状态下观察到 Brownout detector reset，断开舵机并仅以 USB 给 ESP32 / expansion board 供电后软件稳定运行；供电侧原因仍待调查，不修改或关闭 Brownout 保护，相关电源硬件升级延期到独立硬件阶段处理。
- Phase 1-C 真实运动避障、实际阈值、安装方向和制动距离：TODO / PHYSICAL TEST REQUIRED。
- 当前动作接口仍为同步执行，状态等待与传感器模拟是非阻塞的，但后退/转向动作期间无法轮询传感器；保持 baseline 稳定，本阶段不重写 gait。

Phase 1 推荐验证顺序：

1. 阶段 A（已完成）：`DISTANCE_SENSOR_SIMULATION=1`、`OBSTACLE_AVOIDANCE_DRY_RUN=1`；已在真实 ESP32 上验证模拟数据、完整状态机和 Dry Run 执行器隔离。
2. 阶段 B：`DISTANCE_SENSOR_SIMULATION=0`、`OBSTACLE_AVOIDANCE_DRY_RUN=1`，仅验证真实传感器，不允许自动运动。
3. 阶段 C：`DISTANCE_SENSOR_SIMULATION=0`、`OBSTACLE_AVOIDANCE_DRY_RUN=0`，在完成硬件与安全检查后验证真实避障。

## Phase 2：实机避障校准与增强

状态：PLANNED

- 基于实机距离与制动测试校准进入/退出阈值、后退量和转向量。
- 评估非阻塞运动调度，使动作过程中也能持续采样和响应传感器。
- 增加滤波、异常恢复策略与更可靠的转向策略。
- 避障状态与现有 Web 控制的优先级：UNKNOWN。
- 验收场景与安全边界：TODO。

## Phase 3：MPU6050 姿态检测

状态：PLANNED

- 确认模块接线、GPIO、I2C 地址和安装坐标方向。
- 实现加速度与角速度读取、校准和姿态估计。
- 采样频率、滤波算法和标定流程：UNKNOWN。

## Phase 4：姿态稳定

状态：PLANNED

- 在不破坏基础步态的前提下增加姿态补偿。
- 定义补偿范围、控制频率、限幅和失效保护。
- 控制算法及参数：UNKNOWN。
- 实机安全测试方案：TODO。

## Phase 5：行为状态机

状态：PLANNED

- 统一手动控制、行走、避障、姿态保护和故障状态。
- 明确事件、优先级、转换条件和安全停止路径。
- 状态集合和调度方式：UNKNOWN。

## Phase 6：Raspberry Pi 通信

状态：PLANNED

- ESP32 继续负责实时运动控制。
- Raspberry Pi 负责高级指令、视觉和导航任务。
- 通信介质、协议、消息格式、心跳和失联保护：UNKNOWN。
- Raspberry Pi 是否实际加入及其供电方案：TODO。

## Phase 7：视觉导航

状态：PLANNED

- 在 Raspberry Pi 上实现高级视觉与导航能力。
- 摄像头型号、安装位置、算法、地图与算力预算：UNKNOWN。
- ESP32 只接收受约束的高级运动指令，保留底层安全控制。

## Phase 8：语音唤回与高级行为

状态：PLANNED

- 增加语音唤回和高级行为编排。
- 麦克风、音频链路、识别方案和唤回策略：UNKNOWN。
- 高级行为必须服从安全状态和实时运动控制约束。

