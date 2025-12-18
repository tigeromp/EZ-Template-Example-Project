#include "main.h"
#include <cmath>

// Speed settings (out of 127 max)
const int DRIVE_SPEED = 110;   // Speed for forward/backward movement
const int TURN_SPEED = 90;     // Speed for turning in place
const int SWING_SPEED = 110;   // Speed for swing turns (pivot on one side)

// Sets all the PID tuning values and motion settings
void default_constants() {
  // PID constants (Proportional, Integral, Derivative) - adjust these to tune robot movement
  chassis.pid_drive_constants_set(20.0, 0.0, 100.0);      // Forward/backward movement
  chassis.pid_heading_constants_set(11.0, 0.0, 20.0);   // Keep robot straight while driving
  chassis.pid_turn_constants_set(3.0, 0.05, 20.0, 15.0); // Turning in place
  chassis.pid_swing_constants_set(6.0, 0.0, 65.0);      // Swing turns (pivot)

  // Exit conditions - when to stop a movement (time, distance, angle thresholds)
  chassis.pid_turn_exit_condition_set(90_ms, 3_deg, 250_ms, 7_deg, 500_ms, 500_ms);
  chassis.pid_swing_exit_condition_set(90_ms, 3_deg, 250_ms, 7_deg, 500_ms, 500_ms);
  chassis.pid_drive_exit_condition_set(90_ms, 1_in, 250_ms, 3_in, 500_ms, 500_ms);
  
  // Motion chaining - how close to get before starting next movement
  chassis.pid_turn_chain_constant_set(3_deg);
  chassis.pid_swing_chain_constant_set(5_deg);
  chassis.pid_drive_chain_constant_set(3_in);

  // Slew rate - gradually ramp up speed instead of instant (reduces wheel slip)
  chassis.slew_turn_constants_set(3_deg, 70);
  chassis.slew_drive_constants_set(3_in, 70);
  chassis.slew_swing_constants_set(3_in, 80);

  // Always take shortest path when turning (e.g., turn -90° instead of 270°)
  chassis.pid_angle_behavior_set(ez::shortest);
}

// Example: Drive forward, then backward
void drive_example() {
  chassis.pid_drive_set(24_in, DRIVE_SPEED, true);  // Drive 24 inches forward (true = use slew)
  chassis.pid_wait();                                // Wait until movement finishes
  chassis.pid_drive_set(-12_in, DRIVE_SPEED);        // Drive 12 inches backward
  chassis.pid_wait();
  chassis.pid_drive_set(-12_in, DRIVE_SPEED);        // Drive 12 more inches backward
  chassis.pid_wait();
}

// Example: Turn to different angles
void turn_example() {
  chassis.pid_turn_set(90_deg, TURN_SPEED);   // Turn 90 degrees
  chassis.pid_wait();
  chassis.pid_turn_set(45_deg, TURN_SPEED);   // Turn to 45 degrees
  chassis.pid_wait();
  chassis.pid_turn_set(0_deg, TURN_SPEED);    // Turn back to starting angle
  chassis.pid_wait();
}

// Example: Combine driving and turning
void drive_and_turn() {
  chassis.pid_drive_set(24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  chassis.pid_turn_set(45_deg, TURN_SPEED);    // Turn 45 degrees
  chassis.pid_wait();
  chassis.pid_turn_set(-45_deg, TURN_SPEED);   // Turn -45 degrees (back)
  chassis.pid_wait();
  chassis.pid_turn_set(0_deg, TURN_SPEED);     // Face forward again
  chassis.pid_wait();
  chassis.pid_drive_set(-24_in, DRIVE_SPEED, true);  // Drive back to start
  chassis.pid_wait();
}

// Example: Start slow, then speed up partway through movement
void wait_until_change_speed() {
  chassis.pid_drive_set(24_in, 30, true);     // Start driving at slow speed (30)
  chassis.pid_wait_until(6_in);               // Wait until robot has moved 6 inches
  chassis.pid_speed_max_set(DRIVE_SPEED);     // Speed up to full speed for rest
  chassis.pid_wait();
  chassis.pid_turn_set(45_deg, TURN_SPEED);
  chassis.pid_wait();
  chassis.pid_turn_set(-45_deg, TURN_SPEED);
  chassis.pid_wait();
  chassis.pid_turn_set(0_deg, TURN_SPEED);
  chassis.pid_wait();
  chassis.pid_drive_set(-24_in, 30, true);     // Same thing going backward
  chassis.pid_wait_until(-6_in);
  chassis.pid_speed_max_set(DRIVE_SPEED);
  chassis.pid_wait();
}

// Example: Swing turns (pivot on one side instead of turning in place)
void swing_example() {
  chassis.pid_swing_set(ez::LEFT_SWING, 45_deg, SWING_SPEED, 45);   // Lock left side, swing right
  chassis.pid_wait();
  chassis.pid_swing_set(ez::RIGHT_SWING, 0_deg, SWING_SPEED, 45);   // Lock right side, swing left back
  chassis.pid_wait();
  chassis.pid_swing_set(ez::RIGHT_SWING, 45_deg, SWING_SPEED, 45);   // Lock right, swing left
  chassis.pid_wait();
  chassis.pid_swing_set(ez::LEFT_SWING, 0_deg, SWING_SPEED, 45);    // Lock left, swing right back
  chassis.pid_wait();
}

// Example: Motion chaining - blend movements together for smoother motion
void motion_chaining() {
  chassis.pid_drive_set(24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  chassis.pid_turn_set(45_deg, TURN_SPEED);
  chassis.pid_wait_quick_chain();              // Don't wait fully, start next movement early
  chassis.pid_turn_set(-45_deg, TURN_SPEED);
  chassis.pid_wait_quick_chain();              // Blend into next movement
  chassis.pid_turn_set(0_deg, TURN_SPEED);
  chassis.pid_wait();                          // Final movement waits fully
  chassis.pid_drive_set(-24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
}

// Example: Combine all movement types (drive, turn, swing)
void combining_movements() {
  chassis.pid_drive_set(24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  chassis.pid_turn_set(45_deg, TURN_SPEED);
  chassis.pid_wait();
  chassis.pid_swing_set(ez::RIGHT_SWING, -45_deg, SWING_SPEED, 45);  // Swing turn
  chassis.pid_wait();
  chassis.pid_turn_set(0_deg, TURN_SPEED);
  chassis.pid_wait();
  chassis.pid_drive_set(-24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
}

// Helper function: Try to back up if robot gets stuck
void tug(int attempts) {
  for (int i = 0; i < attempts - 1; i++) {
    printf("i - %i", i);
    chassis.pid_drive_set(-12_in, 127);       // Try backing up
    chassis.pid_wait();
    if (chassis.interfered) {                  // If still stuck
      chassis.drive_sensor_reset();
      chassis.pid_drive_set(-2_in, 20);       // Back up slowly
      pros::delay(1000);
    } else {
      return;                                  // Successfully backed up
    }
  }
}

// Example: Handle interference (robot gets blocked/hit)
void interfered_example() {
  chassis.pid_drive_set(24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  if (chassis.interfered) {                   // Check if robot was blocked
    tug(3);                                    // Try to back up 3 times
    return;                                    // Skip rest of routine
  }
  chassis.pid_turn_set(90_deg, TURN_SPEED);   // Only turn if not interfered
  chassis.pid_wait();
}

/**
 * Navigates the robot to a specific coordinate (x, y) from its current position.
 * Uses IMU for heading/rotation tracking and odometry for position tracking.
 * 
 * @param target_x Target X coordinate in inches
 * @param target_y Target Y coordinate in inches
 * @param speed Movement speed (0-127)
 * @param target_heading Optional target heading in degrees (use ANGLE_NOT_SET to not set heading)
 */
void navigate_to_coordinate(double target_x, double target_y, int speed, double target_heading) {
  // Get current robot position using odometry (tracked by chassis)
  pose current_pos = chassis.odom_pose_get();
  
  // Calculate distance and angle to target
  double dx = target_x - current_pos.x;
  double dy = target_y - current_pos.y;
  double distance = sqrt(dx * dx + dy * dy);
  
  // Calculate angle to face target (in degrees)
  // atan2 returns angle in radians, convert to degrees
  // Note: PI constant = 3.14159265358979323846
  const double PI = 3.14159265358979323846;
  double angle_to_target = atan2(dy, dx) * 180.0 / PI;
  
  // Create odom movement structure
  odom movement;
  movement.target.x = target_x;
  movement.target.y = target_y;
  
  // Set target heading (if provided, otherwise let it maintain current heading)
  if (target_heading != ANGLE_NOT_SET) {
    movement.target.theta = target_heading;
  } else {
    movement.target.theta = ANGLE_NOT_SET;  // Don't force a specific heading
  }
  
  // Set movement direction (forward if reasonable, can be adjusted)
  movement.drive_direction = ez::FWD;
  
  // Set speed
  movement.max_xy_speed = speed;
  
  // Use shortest turn behavior
  movement.turn_behavior = ez::shortest;
  
  // Execute the movement
  chassis.pid_odom_set(movement, true);  // true = enable slew for smoother movement
  chassis.pid_wait();  // Wait for movement to complete
}

/**
 * Navigate to coordinate with default speed (overloaded function)
 */
void navigate_to_coordinate(double target_x, double target_y) {
  navigate_to_coordinate(target_x, target_y, DRIVE_SPEED, ANGLE_NOT_SET);
}

/**
 * Navigate to coordinate with custom speed (overloaded function)
 */
void navigate_to_coordinate(double target_x, double target_y, int speed) {
  navigate_to_coordinate(target_x, target_y, speed, ANGLE_NOT_SET);
}

// Example: Navigate to specific coordinates using IMU-based odometry
void navigate_to_coordinates_example() {
  // Reset odometry to starting position (0, 0, 0)
  chassis.odom_reset();
  chassis.drive_imu_reset();
  
  // Navigate to coordinate (24, 36) inches at default speed
  navigate_to_coordinate(24.0, 36.0);
  
  // Navigate to another coordinate (48, 24) at custom speed
  navigate_to_coordinate(48.0, 24.0, 100);
  
  // Navigate to coordinate and face a specific heading (90 degrees)
  navigate_to_coordinate(36.0, 48.0, DRIVE_SPEED, 90.0);
  
  // Return to starting position
  navigate_to_coordinate(0.0, 0.0);
}