#ifndef VL53L1X_DISTANCE_SENSOR_H
#define VL53L1X_DISTANCE_SENSOR_H

#include <Arduino.h>

// Keep simulation enabled until the physical VL53L1X and wiring are verified.
// Set to 0 for the real Adafruit VL53L1X implementation.
#ifndef DISTANCE_SENSOR_SIMULATION
#define DISTANCE_SENSOR_SIMULATION 1
#endif

#if DISTANCE_SENSOR_SIMULATION != 0 && DISTANCE_SENSOR_SIMULATION != 1
#error "DISTANCE_SENSOR_SIMULATION must be 0 or 1"
#endif

#if DISTANCE_SENSOR_SIMULATION == 0
#include <Adafruit_VL53L1X.h>
#endif

enum class DistanceSensorStatus : uint8_t {
  UNINITIALIZED,
  READY_NO_DATA,
  VALID_DATA,
  INVALID_DATA,
  TIMEOUT,
  INIT_FAILED,
  RUNTIME_ERROR
};

class VL53L1XDistanceSensor {
 public:
  VL53L1XDistanceSensor();

  bool begin();
  bool update();
  uint16_t getDistanceMm() const;
  bool isDistanceValid() const;
  bool isInitialized() const;
  DistanceSensorStatus getStatus() const;

 private:
#if DISTANCE_SENSOR_SIMULATION == 0
  void clearMeasurementInterrupt();
  void reportDriverError(const __FlashStringHelper* operation,
                         VL53L1X_ERROR status);
  void reportPeriodicDriverWarning(const __FlashStringHelper* operation,
                                   VL53L1X_ERROR status,
                                   uint32_t nowMs);

  Adafruit_VL53L1X sensor_;
#endif
  void logDistance(uint32_t nowMs);

  bool initialized_;
  bool distanceValid_;
  bool timeoutReported_;
  bool warningReported_;
  bool distanceLogStarted_;
  uint16_t distanceMm_;
  DistanceSensorStatus status_;
#if DISTANCE_SENSOR_SIMULATION == 1
  size_t simulationSampleIndex_;
#endif
  uint32_t lastDataReadyMs_;
  uint32_t lastWarningMs_;
  uint32_t lastDistanceLogMs_;
};

#endif
