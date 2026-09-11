#ifndef OBSTACLE_AVOIDANCE_H
#define OBSTACLE_AVOIDANCE_H

#include <Arduino.h>

#include "VL53L1XDistanceSensor.h"
#include "minikame.h"

// Keep automatic avoidance actions disabled during software-only validation.
// Set to 0 only for the final, physically supervised avoidance test.
#ifndef OBSTACLE_AVOIDANCE_DRY_RUN
#define OBSTACLE_AVOIDANCE_DRY_RUN 1
#endif

#if OBSTACLE_AVOIDANCE_DRY_RUN != 0 && OBSTACLE_AVOIDANCE_DRY_RUN != 1
#error "OBSTACLE_AVOIDANCE_DRY_RUN must be 0 or 1"
#endif

enum class AvoidanceState : uint8_t {
  CLEAR,
  OBSTACLE_DETECTED,
  BACKING_UP,
  TURNING,
  RECOVERING,
  SENSOR_FAULT
};

class ObstacleAvoidanceController {
 public:
  ObstacleAvoidanceController(MiniKame& robot,
                              const VL53L1XDistanceSensor& distanceSensor);

  void begin();
  void update(bool distanceUpdated);
  bool canMoveForward() const;
  AvoidanceState getState() const;
  const char* getStateName() const;

 private:
  enum class AvoidanceAction : uint8_t {
    STOP,
    BACKWARD,
    TURN_RIGHT,
    RECOVER,
    HOME_SAFE
  };

  void transitionTo(AvoidanceState nextState);
  void updateSafeDistanceConfirmation(uint32_t nowMs);
  void requestAction(AvoidanceAction action);
  static const char* stateName(AvoidanceState state);
  static const char* actionName(AvoidanceAction action);

  MiniKame& robot_;
  const VL53L1XDistanceSensor& distanceSensor_;
  AvoidanceState state_;
  bool started_;
  bool safeDistancePending_;
  uint32_t stateEnteredAtMs_;
  uint32_t safeDistanceSinceMs_;
};

#endif
