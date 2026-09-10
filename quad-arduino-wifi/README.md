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

