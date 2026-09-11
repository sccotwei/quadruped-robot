#include "ObstacleAvoidance.h"

namespace {

// Initial tuning values only. Calibrate with the physical VL53L1X and the
// robot's measured stopping distance before relying on autonomous avoidance.
constexpr uint16_t kObstacleEnterMm = 250;
constexpr uint16_t kObstacleExitMm = 350;

constexpr uint32_t kStoppedSettleMs = 250;
constexpr uint32_t kPostMotionSettleMs = 100;
constexpr uint32_t kSafeDistanceConfirmMs = 400;

// Reuse the Phase 0 action implementations without changing their internal
// servo, amplitude, offset, or phase values. Calls are currently synchronous.
constexpr float kBackupSteps = 0.5F;
constexpr int kBackupPeriodMs = 600;
constexpr float kTurnSteps = 0.5F;
constexpr int kTurnPeriodMs = 600;

static_assert(kObstacleExitMm > kObstacleEnterMm,
              "Obstacle hysteresis exit must exceed enter threshold");

}  // namespace

ObstacleAvoidanceController::ObstacleAvoidanceController(
    MiniKame& robot, const VL53L1XDistanceSensor& distanceSensor)
    : robot_(robot),
      distanceSensor_(distanceSensor),
      state_(AvoidanceState::SENSOR_FAULT),
      started_(false),
      safeDistancePending_(false),
      stateEnteredAtMs_(0),
      safeDistanceSinceMs_(0) {}

void ObstacleAvoidanceController::begin() {
  started_ = true;
  state_ = AvoidanceState::SENSOR_FAULT;
  stateEnteredAtMs_ = millis();
  safeDistancePending_ = false;
  requestAction(AvoidanceAction::HOME_SAFE);
  Serial.println(
      F("[AVOID] initialized in SENSOR_FAULT; waiting for safe data"));
}

void ObstacleAvoidanceController::update(bool distanceUpdated) {
  if (!started_) {
    return;
  }

  const uint32_t nowMs = millis();
  if (!distanceSensor_.isInitialized() ||
      !distanceSensor_.isDistanceValid()) {
    if (state_ != AvoidanceState::SENSOR_FAULT) {
      transitionTo(AvoidanceState::SENSOR_FAULT);
    }
    return;
  }

  const uint16_t distanceMm = distanceSensor_.getDistanceMm();

  switch (state_) {
    case AvoidanceState::CLEAR:
      if (distanceUpdated && distanceMm <= kObstacleEnterMm) {
        transitionTo(AvoidanceState::OBSTACLE_DETECTED);
      }
      break;

    case AvoidanceState::OBSTACLE_DETECTED:
      if (nowMs - stateEnteredAtMs_ >= kStoppedSettleMs) {
        transitionTo(AvoidanceState::BACKING_UP);
      }
      break;

    case AvoidanceState::BACKING_UP:
      if (nowMs - stateEnteredAtMs_ >= kPostMotionSettleMs) {
        transitionTo(AvoidanceState::TURNING);
      }
      break;

    case AvoidanceState::TURNING:
      if (nowMs - stateEnteredAtMs_ >= kPostMotionSettleMs) {
        transitionTo(AvoidanceState::RECOVERING);
      }
      break;

    case AvoidanceState::RECOVERING:
      if (!distanceUpdated) {
        break;
      }
      if (distanceMm <= kObstacleEnterMm) {
        transitionTo(AvoidanceState::OBSTACLE_DETECTED);
      } else {
        updateSafeDistanceConfirmation(nowMs);
      }
      break;

    case AvoidanceState::SENSOR_FAULT:
      if (!distanceUpdated) {
        break;
      }
      if (distanceMm <= kObstacleEnterMm) {
        transitionTo(AvoidanceState::OBSTACLE_DETECTED);
      } else {
        updateSafeDistanceConfirmation(nowMs);
      }
      break;
  }
}

bool ObstacleAvoidanceController::canMoveForward() const {
  return started_ && state_ == AvoidanceState::CLEAR &&
         distanceSensor_.isInitialized() &&
         distanceSensor_.isDistanceValid() &&
         distanceSensor_.getDistanceMm() > kObstacleEnterMm;
}

AvoidanceState ObstacleAvoidanceController::getState() const { return state_; }

const char* ObstacleAvoidanceController::getStateName() const {
  return stateName(state_);
}

void ObstacleAvoidanceController::transitionTo(AvoidanceState nextState) {
  if (state_ == nextState) {
    return;
  }

  Serial.print(F("[AVOID] "));
  Serial.print(stateName(state_));
  Serial.print(F(" -> "));
  Serial.println(stateName(nextState));

  state_ = nextState;
  stateEnteredAtMs_ = millis();
  safeDistancePending_ = false;

  switch (state_) {
    case AvoidanceState::OBSTACLE_DETECTED:
      requestAction(AvoidanceAction::STOP);
      break;

    case AvoidanceState::SENSOR_FAULT:
      requestAction(AvoidanceAction::HOME_SAFE);
      break;

    case AvoidanceState::BACKING_UP:
      requestAction(AvoidanceAction::BACKWARD);
      requestAction(AvoidanceAction::STOP);
      stateEnteredAtMs_ = millis();
      break;

    case AvoidanceState::TURNING:
      requestAction(AvoidanceAction::TURN_RIGHT);
      requestAction(AvoidanceAction::STOP);
      stateEnteredAtMs_ = millis();
      break;

    case AvoidanceState::RECOVERING:
      requestAction(AvoidanceAction::RECOVER);
      break;

    case AvoidanceState::CLEAR:
      break;
  }
}

void ObstacleAvoidanceController::updateSafeDistanceConfirmation(
    uint32_t nowMs) {
  if (distanceSensor_.getDistanceMm() < kObstacleExitMm) {
    safeDistancePending_ = false;
    return;
  }

  if (!safeDistancePending_) {
    safeDistancePending_ = true;
    safeDistanceSinceMs_ = nowMs;
    return;
  }

  if (nowMs - safeDistanceSinceMs_ >= kSafeDistanceConfirmMs) {
    transitionTo(AvoidanceState::CLEAR);
  }
}

void ObstacleAvoidanceController::requestAction(AvoidanceAction action) {
#if OBSTACLE_AVOIDANCE_DRY_RUN == 1
  Serial.print(F("[AVOID][DRYRUN] action="));
  Serial.println(actionName(action));
#else
  switch (action) {
    case AvoidanceAction::STOP:
    case AvoidanceAction::HOME_SAFE:
      robot_.home();
      break;

    case AvoidanceAction::BACKWARD:
      robot_.backward(kBackupSteps, kBackupPeriodMs);
      break;

    case AvoidanceAction::TURN_RIGHT:
      robot_.turnR(kTurnSteps, kTurnPeriodMs);
      break;

    case AvoidanceAction::RECOVER:
      break;
  }
#endif
}

const char* ObstacleAvoidanceController::stateName(AvoidanceState state) {
  switch (state) {
    case AvoidanceState::CLEAR:
      return "CLEAR";
    case AvoidanceState::OBSTACLE_DETECTED:
      return "OBSTACLE_DETECTED";
    case AvoidanceState::BACKING_UP:
      return "BACKING_UP";
    case AvoidanceState::TURNING:
      return "TURNING";
    case AvoidanceState::RECOVERING:
      return "RECOVERING";
    case AvoidanceState::SENSOR_FAULT:
      return "SENSOR_FAULT";
  }

  return "UNKNOWN";
}

const char* ObstacleAvoidanceController::actionName(AvoidanceAction action) {
  switch (action) {
    case AvoidanceAction::STOP:
      return "STOP";
    case AvoidanceAction::BACKWARD:
      return "BACKWARD";
    case AvoidanceAction::TURN_RIGHT:
      return "TURN_RIGHT";
    case AvoidanceAction::RECOVER:
      return "RECOVER";
    case AvoidanceAction::HOME_SAFE:
      return "HOME_SAFE";
  }

  return "UNKNOWN";
}
