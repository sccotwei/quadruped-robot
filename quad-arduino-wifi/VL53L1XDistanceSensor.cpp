#include "VL53L1XDistanceSensor.h"

#if DISTANCE_SENSOR_SIMULATION == 0
#include <Wire.h>
#endif

namespace {

#if DISTANCE_SENSOR_SIMULATION == 1
constexpr uint16_t kSimulatedDistancesMm[] = {800, 600, 450, 350,
                                               280, 220, 180, 150};
constexpr size_t kSimulatedDistanceCount =
    sizeof(kSimulatedDistancesMm) / sizeof(kSimulatedDistancesMm[0]);
constexpr uint32_t kSimulationSampleIntervalMs = 200;
#else
constexpr uint8_t kSdaPin = 21;
constexpr uint8_t kSclPin = 22;
constexpr uint8_t kDefaultI2cAddress = 0x29;
constexpr uint32_t kMeasurementTimeoutMs = 1000;
constexpr uint32_t kWarningReportIntervalMs = 1000;
#endif
constexpr uint32_t kDistanceLogIntervalMs = 200;

}  // namespace

VL53L1XDistanceSensor::VL53L1XDistanceSensor()
    : initialized_(false),
      distanceValid_(false),
      timeoutReported_(false),
      warningReported_(false),
      distanceLogStarted_(false),
      distanceMm_(0),
      status_(DistanceSensorStatus::UNINITIALIZED),
#if DISTANCE_SENSOR_SIMULATION == 1
      simulationSampleIndex_(0),
#endif
      lastDataReadyMs_(0),
      lastWarningMs_(0),
      lastDistanceLogMs_(0) {}

bool VL53L1XDistanceSensor::begin() {
  initialized_ = false;
  distanceValid_ = false;
  timeoutReported_ = false;
  warningReported_ = false;
  distanceLogStarted_ = false;
  distanceMm_ = 0;
  status_ = DistanceSensorStatus::UNINITIALIZED;
  lastDataReadyMs_ = millis();
  lastWarningMs_ = 0;
  lastDistanceLogMs_ = 0;

#if DISTANCE_SENSOR_SIMULATION == 1
  simulationSampleIndex_ = 0;
  initialized_ = true;
  status_ = DistanceSensorStatus::READY_NO_DATA;
  Serial.println(F("[TOF][SIM] initialized; hardware access disabled"));
  return true;
#else
  if (!Wire.begin(kSdaPin, kSclPin)) {
    status_ = DistanceSensorStatus::INIT_FAILED;
    Serial.println(F("[TOF][ERROR] I2C init failed (SDA=21, SCL=22)"));
    return false;
  }

  if (!sensor_.begin(kDefaultI2cAddress, &Wire)) {
    reportDriverError(F("sensor initialization failed"), sensor_.vl_status);
    status_ = DistanceSensorStatus::INIT_FAILED;
    return false;
  }

  if (!sensor_.startRanging()) {
    reportDriverError(F("could not start ranging"), sensor_.vl_status);
    status_ = DistanceSensorStatus::INIT_FAILED;
    return false;
  }

  initialized_ = true;
  status_ = DistanceSensorStatus::READY_NO_DATA;
  lastDataReadyMs_ = millis();
  Serial.println(F("[TOF] ready; ranging at I2C address 0x29"));
  return true;
#endif
}

bool VL53L1XDistanceSensor::update() {
  if (!initialized_) {
    return false;
  }

  const uint32_t nowMs = millis();

#if DISTANCE_SENSOR_SIMULATION == 1
  if (nowMs - lastDataReadyMs_ < kSimulationSampleIntervalMs) {
    return false;
  }

  lastDataReadyMs_ = nowMs;
  distanceMm_ = kSimulatedDistancesMm[simulationSampleIndex_];
  simulationSampleIndex_ =
      (simulationSampleIndex_ + 1) % kSimulatedDistanceCount;
  distanceValid_ = true;
  status_ = DistanceSensorStatus::VALID_DATA;
  logDistance(nowMs);
  return true;
#else
  const bool dataReady = sensor_.dataReady();

  if (sensor_.vl_status != VL53L1X_ERROR_NONE) {
    distanceValid_ = false;
    status_ = DistanceSensorStatus::RUNTIME_ERROR;
    reportPeriodicDriverWarning(F("data-ready check failed"),
                                sensor_.vl_status, nowMs);
    return false;
  }

  if (!dataReady) {
    if (!timeoutReported_ &&
        nowMs - lastDataReadyMs_ >= kMeasurementTimeoutMs) {
      distanceValid_ = false;
      status_ = DistanceSensorStatus::TIMEOUT;
      Serial.println(F("[TOF][WARN] measurement timeout"));
      timeoutReported_ = true;
    }
    return false;
  }

  lastDataReadyMs_ = nowMs;
  timeoutReported_ = false;

  const int16_t measuredDistanceMm = sensor_.distance();
  if (measuredDistanceMm < 0) {
    distanceValid_ = false;
    status_ = DistanceSensorStatus::INVALID_DATA;
    reportPeriodicDriverWarning(F("invalid measurement"), sensor_.vl_status,
                                nowMs);
    clearMeasurementInterrupt();
    return false;
  }

  clearMeasurementInterrupt();
  if (!initialized_) {
    return false;
  }

  distanceMm_ = static_cast<uint16_t>(measuredDistanceMm);
  distanceValid_ = true;
  status_ = DistanceSensorStatus::VALID_DATA;
  logDistance(nowMs);
  return true;
#endif
}

uint16_t VL53L1XDistanceSensor::getDistanceMm() const { return distanceMm_; }

bool VL53L1XDistanceSensor::isDistanceValid() const {
  return distanceValid_;
}

bool VL53L1XDistanceSensor::isInitialized() const { return initialized_; }

DistanceSensorStatus VL53L1XDistanceSensor::getStatus() const {
  return status_;
}

void VL53L1XDistanceSensor::logDistance(uint32_t nowMs) {
  if (distanceLogStarted_ &&
      nowMs - lastDistanceLogMs_ < kDistanceLogIntervalMs) {
    return;
  }

  distanceLogStarted_ = true;
  lastDistanceLogMs_ = nowMs;
  Serial.print(F("[TOF]"));
#if DISTANCE_SENSOR_SIMULATION == 1
  Serial.print(F("[SIM]"));
#endif
  Serial.print(F(" distance="));
  Serial.print(distanceMm_);
  Serial.println(F("mm"));
}

#if DISTANCE_SENSOR_SIMULATION == 0
void VL53L1XDistanceSensor::clearMeasurementInterrupt() {
  if (!sensor_.clearInterrupt()) {
    distanceValid_ = false;
    status_ = DistanceSensorStatus::RUNTIME_ERROR;
    reportPeriodicDriverWarning(F("interrupt clear failed"), sensor_.vl_status,
                                millis());
    initialized_ = false;
  }
}

void VL53L1XDistanceSensor::reportDriverError(
    const __FlashStringHelper* operation, VL53L1X_ERROR status) {
  Serial.print(F("[TOF][ERROR] "));
  Serial.print(operation);
  Serial.print(F(", driver_status="));
  Serial.println(static_cast<int>(status));
}

void VL53L1XDistanceSensor::reportPeriodicDriverWarning(
    const __FlashStringHelper* operation, VL53L1X_ERROR status,
    uint32_t nowMs) {
  if (warningReported_ &&
      nowMs - lastWarningMs_ < kWarningReportIntervalMs) {
    return;
  }

  warningReported_ = true;
  lastWarningMs_ = nowMs;
  Serial.print(F("[TOF][WARN] "));
  Serial.print(operation);
  Serial.print(F(", driver_status="));
  Serial.println(static_cast<int>(status));
}
#endif
