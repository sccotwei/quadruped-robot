#ifndef CONFIG_H
#define CONFIG_H

#include <WiFi.h>

// Wi-Fi mode: true for AP mode, false for STA mode.
const bool USE_AP_MODE = false;

// STA mode configuration.
const char *ssid = "YOUR_WIFI_SSID";
const char *password = "YOUR_WIFI_PASSWORD";
IPAddress local_ip(192, 168, 1, 192);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

// AP mode configuration.
const char *ap_ssid = "QUADRUPED_AP";
const char *ap_password = "CHANGE_ME";
IPAddress ap_local_ip(192, 168, 4, 1);
IPAddress ap_gateway(192, 168, 4, 1);
IPAddress ap_subnet(255, 255, 255, 0);

#endif

