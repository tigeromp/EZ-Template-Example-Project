#include "main.h"

// Robot setup - defines the drive motors, IMU port, wheel size, and motor speed
ez::Drive chassis(
    {-1, -2, -4},        // Left side motors (negative = reversed)
    {11, 12, 14},    // Right side motors (negative = reversed)
    7,                 // IMU port number
    3.125,             // Wheel diameter in inches
    343);              // Motor RPM (based on gear ratio)

// IMU sensor on port 10 - used for turning and keeping straight
pros::Imu imu(10);

// Runs once when the robot starts up - sets up everything
void initialize() {
  pros::delay(500);  // Wait for ports to configure

  // Driver control settings
  chassis.opcontrol_curve_buttons_toggle(true);   // Allow changing joystick curve with buttons
  chassis.opcontrol_drive_activebrake_set(0.0);   // Disable active braking (0 = off)
  chassis.opcontrol_curve_default_set(0.0, 0.0); // Default joystick curve (linear)

  // Load PID tuning values from autons.cpp
  default_constants();

  // Add autonomous routines to the selector menu
  ez::as::auton_selector.autons_add({
      {"Drive", drive_example},
      {"Turn", turn_example},
      {"Drive and Turn", drive_and_turn},
      {"Wait Until Change Speed", wait_until_change_speed},
      {"Swing", swing_example},
      {"Motion Chaining", motion_chaining},
      {"Combining Movements", combining_movements},
      {"Interference", interfered_example},
  });

  // Start up the chassis and auton selector
  chassis.initialize();
  ez::as::initialize();
  
  // Wait for IMU to calibrate, then rumble controller
  pros::delay(100);
  master.rumble(chassis.drive_imu_calibrated() ? "." : "---");
}

// Runs when robot is disabled (between matches)
void disabled() {}

// Runs right before autonomous starts in competition
void competition_initialize() {}

// Runs during the 15-second autonomous period
void autonomous() {
  // Reset everything to starting position
  chassis.pid_targets_reset();      // Clear any pending movements
  chassis.drive_imu_reset();         // Reset gyro to 0 degrees
  chassis.drive_sensor_reset();      // Reset motor encoders to 0
  chassis.drive_brake_set(MOTOR_BRAKE_HOLD);  // Lock motors when stopped

  // Run the autonomous routine selected from the menu
  ez::as::auton_selector.selected_auton_call();
}

// Continuously displays IMU/gyro values on the brain screen
void ez_screen_task() {
  while (true) {
    // Check if IMU is still calibrating
    if (imu.get_status() == pros::ImuStatus::calibrating) {
      ez::screen_print("IMU Calibrating...\nPlease wait", 1);
    } else {
      // Get rotation rates from gyroscope
      pros::imu_gyro_s_t gyro = imu.get_gyro_rate();
      
      // Check for sensor errors
      if (gyro.x == PROS_ERR_F || gyro.y == PROS_ERR_F || gyro.z == PROS_ERR_F) {
        ez::screen_print("Gyro Error\nCheck Port 10", 1);
      } else {
        // Display X, Y, Z rotation speeds in degrees per second
        std::string gyro_text = std::string("Gyroscope (Port 10):\n") +
                                "X: " + util::to_string_with_precision(gyro.x, 2) + " deg/s\n" +
                                "Y: " + util::to_string_with_precision(gyro.y, 2) + " deg/s\n" +
                                "Z: " + util::to_string_with_precision(gyro.z, 2) + " deg/s";
        ez::screen_print(gyro_text, 1);
      }
    }

    pros::delay(ez::util::DELAY_TIME);
  }
}
pros::Task ezScreenTask(ez_screen_task);  // Runs this function in background

// Extra features for testing (only works when NOT in competition mode)
void ez_template_extras() {
  if (!pros::competition::is_connected()) {
    // Press X to open/close PID tuner (adjust PID values on screen)
    if (master.get_digital_new_press(DIGITAL_X))
      chassis.pid_tuner_toggle();

    // Press DOWN + B to test autonomous routine during driver control
    if (master.get_digital(DIGITAL_B) && master.get_digital(DIGITAL_DOWN)) {
      pros::motor_brake_mode_e_t preference = chassis.drive_brake_get();
      autonomous();
      chassis.drive_brake_set(preference);
    }

    // Update PID tuner if it's open
    chassis.pid_tuner_iterate();
  } else {
    // Disable PID tuner during competition
    if (chassis.pid_tuner_enabled())
      chassis.pid_tuner_disable();
  }
}

// Runs during the 1 minute 45 second driver control period
void opcontrol() {
  // Set motors to coast when not moving (easier to push robot)
  chassis.drive_brake_set(MOTOR_BRAKE_COAST);

  while (true) {
    // Check for extra features (PID tuner, test auton)
    ez_template_extras();

    // Read joysticks and drive the robot:
    // - Left joystick: forward / backward
    // - Right joystick: turn left / right
    chassis.opcontrol_arcade_standard(ez::SPLIT);

    pros::delay(ez::util::DELAY_TIME);
  }
}
