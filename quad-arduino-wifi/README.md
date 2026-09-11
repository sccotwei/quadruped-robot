# Quad 四足机器人 Arduino Wi-Fi 版代码

## 相关链接

- **本项目的 MicroPython Wi-Fi 版本**：[仓库链接](https://github.com/AniPython/quad-mpy)
- **B站**：[视频链接](https://www.bilibili.com/video/BV1Lzo4YnEEt/)

## 依赖的开发板

1. ESP32（by Espressif Systems）

   如果在线安装失败，可以参考：[Arduino ESP32 离线安装](https://arduino.me/a/esp32)

## 依赖的库

1. ESP32Servo
2. ArduinoJson
3. Adafruit VL53L1X（仅真实传感器模式需要，并依赖 Adafruit BusIO）

## 距离传感器模式

`VL53L1XDistanceSensor.h` 中的 `DISTANCE_SENSOR_SIMULATION` 控制距离来源，
`ObstacleAvoidance.h` 中的 `OBSTACLE_AVOIDANCE_DRY_RUN` 控制避障动作是否实际执行。
当前推荐的软件测试配置为：

```cpp
#define DISTANCE_SENSOR_SIMULATION 1
#define OBSTACLE_AVOIDANCE_DRY_RUN 1
```

该配置不访问 VL53L1X，不允许避障状态机自动驱动机器人，只输出模拟距离、状态转换和 `[AVOID][DRYRUN]` 动作日志。Dry Run 只拦截 `ObstacleAvoidance` 产生的动作；正常舵机初始化和用户主动 Web 控制保持原样，因此实体机器人仍应架空并准备随时断电。

Phase 1-A 已使用上述配置在真实 ESP32 上完成编译、上传和运行验证：模拟距离正常循环，避障状态机完整经历 `CLEAR -> OBSTACLE_DETECTED -> BACKING_UP -> TURNING -> RECOVERING -> CLEAR`，并确认 Dry Run 下没有避障模块引发的真实舵机动作。这只验证软件仿真路径，不代表真实 VL53L1X、I2C 接线或真实运动避障已经验证。

真实测试必须按以下顺序推进：

| 阶段 | `DISTANCE_SENSOR_SIMULATION` | `OBSTACLE_AVOIDANCE_DRY_RUN` | 目的 |
|---|---:|---:|---|
| A（已完成） | 1 | 1 | 已在真实 ESP32 上验证模拟数据、完整状态机和 Dry Run 执行器隔离 |
| B | 0 | 1 | 验证真实 VL53L1X、I2C 和距离数据，仍禁止自动避障动作 |
| C | 0 | 0 | 完成供电、接线、距离和安全措施验证后，进行最终真实避障测试 |

进入阶段 B 前必须先阅读 `docs/HARDWARE.md`；其中 VCC 电压仍待万用表确认，禁止仅根据文档直接通电。真实传感器模式还需要 Adafruit VL53L1X、Adafruit BusIO、Wire 和 GPIO21 / GPIO22。

尚未完成：Phase 1-B 真实 VL53L1X 测试、expansion-board VCC 电压测量、D21 / D22 物理 I2C 验证、舵机 / Brownout 供电调查，以及 Phase 1-C 真实运动避障。实测中，连接全部舵机时曾出现 Brownout detector reset；断开舵机并仅使用 USB 给 ESP32 / expansion board 供电后程序稳定运行。该现象当前仅作为供电侧待调查事项，不应关闭 Brownout 保护或据此修改舵机供电逻辑；相关电源硬件升级延期到后续独立硬件阶段。

## 首次编译前配置

将示例配置复制为本地配置：

```text
Config.example.h
->
Config.h
```

然后在本地 `Config.h` 中填写自己的 Wi-Fi 配置。`Config.h` 包含本机凭据，已被 Git 忽略，不应提交到 Git。

## Wi-Fi 配置说明

### 1. 选择 Wi-Fi 模式

在 `Config.h` 中选择 AP 或 STA 模式：

```cpp
// true 为 AP 模式，false 为 STA 模式
const bool USE_AP_MODE = false;
```

### 2. STA 模式

STA 模式用于连接 2.4 GHz 路由器。请将占位符替换为自己的配置：

```cpp
const char *ssid = "YOUR_WIFI_SSID";
const char *password = "YOUR_WIFI_PASSWORD";
IPAddress local_ip(192, 168, 1, 192);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
```

静态 IP、网关和子网必须根据实际网络填写。无法确认的信息为 `UNKNOWN`，不得直接猜测。

连接成功后，在浏览器中访问 `Config.h` 中配置的 `local_ip`。

### 3. AP 模式

AP 模式由 ESP32 创建本地热点。请将密码占位符替换为自己的安全密码：

```cpp
const char *ap_ssid = "QUADRUPED_AP";
const char *ap_password = "CHANGE_ME";
IPAddress ap_local_ip(192, 168, 4, 1);
IPAddress ap_gateway(192, 168, 4, 1);
IPAddress ap_subnet(255, 255, 255, 0);
```

连接热点后，在浏览器中访问 `Config.h` 中配置的 `ap_local_ip`。

## 安全提示

- 不要将真实 SSID、Wi-Fi 密码、API Key 或 Token 写入 README。
- 不要提交 `Config.h`。
- 只提交使用明显占位符的 `Config.example.h`。

