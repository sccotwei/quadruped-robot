# Hardware

## 当前已知硬件

| 部件 | 当前状态 | 用途 |
|---|---|---|
| ESP32 主控 | 已存在 | 继续负责实时运动控制 |
| 四足机器人机构 | 已存在，基础行走可工作 | 运动平台 |
| VL53L1X 激光测距模块 | Phase 1 软件已集成，尚未实机验证 | 距离采集、模拟输入与基础前向避障 |
| MPU6050 | 已知、尚未集成 | 计划用于姿态检测 |
| 3.7V 1000mAh 锂电池 | 已存在 | 系统供电 |
| Raspberry Pi 4B 2GB | 后续可能增加 | 计划负责高级视觉与导航 |

## 控制职责

- ESP32：实时运动控制、现有舵机控制，以及后续底层传感与执行闭环。
- Raspberry Pi：计划负责高级视觉、导航与高级行为决策。
- ESP32 与 Raspberry Pi 的通信方式：UNKNOWN。

## VL53L1X Phase 1 预计接线

**HARDWARE TESTED: NO**

> VCC 电压待用万用表实测确认，禁止根据此文档直接通电。

| VL53L1X 引脚 | ESP32 连接 | 状态 |
|---|---|---|
| VCC | expansion board VCC | TODO：万用表确认实际电压后才能通电 |
| GND | expansion board GND | TODO：实机上电前确认共地 |
| SDA | GPIO21 / D21 | 代码无已知冲突；物理接线未验证 |
| SCL | GPIO22 / D22 | 代码无已知冲突；物理接线未验证 |
| XSHUT | 暂不使用 | 软件方案如此；物理未验证 |
| INT / GPIO1 | 暂不使用 | 软件轮询 data-ready；物理未验证 |

- 当前代码中的 8 路舵机 GPIO 为 `12/16/25/18/13/17/26/19`，LED 为 GPIO2；静态搜索未发现 GPIO21 / GPIO22 被现有功能占用。
- 上述结果只代表仓库代码检查，不代表 ESP32 板型、扩展板走线或实体接线已经验证。
- 软件尝试 VL53L1X 出厂默认 7-bit I2C 地址 `0x29`；实机是否在该地址应答：UNKNOWN。
- 安装位置和朝向：UNKNOWN。
- Phase 1 默认启用模拟距离；真实模式才会访问 I2C 和 VL53L1X。
- 基础避障复用现有 `home()`、`backward()` 和 `turnR()`，未改变舵机 GPIO、步态参数或供电逻辑。

## 未确认信息

- ESP32 具体型号或开发板变体：UNKNOWN
- 舵机型号：UNKNOWN
- 舵机额定电压和峰值电流：UNKNOWN
- 舵机数量的硬件实物确认：TODO
- GPIO 与实物接线对应关系：UNKNOWN；TODO 在不改变现有可工作配置的前提下核对实物
- expansion board VCC 实际电压及 VL53L1X 供电兼容性：UNKNOWN；通电前必须实测
- GPIO21 / GPIO22 的扩展板物理连通性：UNKNOWN
- VL53L1X 实机 I2C 地址响应：UNKNOWN
- MPU6050 GPIO、I2C 总线及地址：UNKNOWN
- MPU6050 安装位置和坐标方向：UNKNOWN
- 电池保护、电源开关、稳压和舵机独立供电方案：UNKNOWN
- ESP32 与 Raspberry Pi 的供电隔离和共地方案：UNKNOWN
- 具体接线图的实物验证状态：TODO

## 硬件变更规则

- 不根据常见接法猜测 GPIO 或总线。
- 不根据外观或代码猜测舵机型号。
- 新接线必须先记录并经实物确认，再进入软件实现。
- 任何会影响现有基础行走的供电或舵机变更，都必须先定义回退方案。

