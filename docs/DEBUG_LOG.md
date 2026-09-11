# Debug Log

用于记录可复现的问题、诊断过程、验证结果和遗留事项。硬件或测试条件未确认时必须写为 `UNKNOWN` 或 `TODO`。

## 2026-09-10 — 工程管理 baseline

- 阶段：Phase 0
- 已知状态：四足机器人基础行走可以工作。
- 完成内容：初始化工程管理结构，建立硬件、架构、路线图和调试记录文档。
- 运动逻辑变更：无。
- 舵机参数变更：无。
- GPIO 变更：无。
- VL53L1X 开发：未开始。
- 固件编译验证：TODO。
- 实机回归测试：TODO。
- Arduino、ESP32 Core 和依赖库版本：UNKNOWN。

## 2026-09-11 — Phase 1-A watchdog reboot loop

- 所属 Phase：Phase 1-A
- 硬件环境：真实 ESP32；VL53L1X 未连接；其他板型、供电和接线信息 UNKNOWN
- 测试配置：预期 `DISTANCE_SENSOR_SIMULATION=1`、`OBSTACLE_AVOIDANCE_DRY_RUN=1`
- 问题现象：固件成功编译并上传，但 Boot ROM 以 115200 baud 持续报告 `rst:0x8 (TG1WDT_SYS_RESET)` 后重启
- 应用串口：`Serial.begin(9600)`；与 Boot ROM 的 115200 baud 不同
- 静态诊断：模拟测距不包含 Wire / Adafruit 初始化；Dry Run 不执行避障动作；距离更新和状态机单次调用均为有限路径
- 已知 watchdog 风险：`MiniKame::moveServos()` 含无 `yield()` 的忙等待，但当前启动路径和 Dry Run 自动避障路径均不调用它
- 其他观察：STA Wi-Fi 等待循环有 20 次上限且每次调用 `delay(1000)`；WebServer 初始化重复两次，但这是 Phase 0 已存在路径
- 根因：UNKNOWN；尚无日志证明 reset 发生于哪个初始化步骤
- 本轮处理：在距离传感器、Wi-Fi、两次 WebServer、`robot.init()`、`robot.home()`、避障控制器前后增加 `[BOOT]` 路标；loop 完整执行后每 1000 ms 输出 heartbeat
- 编译验证：已由用户使用 `DISTANCE_SENSOR_SIMULATION=1`、`OBSTACLE_AVOIDANCE_DRY_RUN=1` 成功编译并上传至真实 ESP32
- 实机验证：Phase 1-A 软件仿真路径已通过；模拟距离、完整避障状态循环与 Dry Run 执行器隔离均符合预期
- 运动逻辑、舵机参数和 GPIO 变更：无
- 后续实机结果：以 `DISTANCE_SENSOR_SIMULATION=1`、`OBSTACLE_AVOIDANCE_DRY_RUN=1` 成功编译、上传并稳定运行；模拟距离循环、完整避障状态循环及 Dry Run 执行器隔离均已验证
- 供电观察：连接全部舵机时曾出现 `Brownout detector reset`；断开舵机并仅使用 USB 给 ESP32 / expansion board 供电后程序稳定运行
- 结论边界：此前 `TG1WDT_SYS_RESET` 的具体根因仍为 UNKNOWN；Brownout 现象暂列为供电侧待调查问题，相关电源硬件升级延期处理；未修改 Brownout 保护或舵机供电逻辑
- 遗留事项：Phase 1-B 真实 VL53L1X、expansion-board VCC 实测、D21 / D22 物理 I2C、舵机供电 / Brownout 调查及 Phase 1-C 真实运动避障

## 后续记录模板

### YYYY-MM-DD — 标题

- 所属 Phase：UNKNOWN
- 硬件环境：UNKNOWN
- 固件版本或 Git commit：UNKNOWN
- 问题现象：TODO
- 复现步骤：TODO
- 预期行为：TODO
- 实际行为：TODO
- 诊断过程：TODO
- 根因：UNKNOWN
- 处理结果：TODO
- 编译验证：TODO
- 实机验证：TODO
- 遗留事项：TODO
