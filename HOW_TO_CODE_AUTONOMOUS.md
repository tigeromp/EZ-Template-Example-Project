# How to Code Autonomous Routines with EZ-Template

This guide will help you write autonomous routines for your VEX robot using the EZ-Template library.

## Table of Contents
1. [Understanding the Structure](#understanding-the-structure)
2. [Basic Movement Commands](#basic-movement-commands)
3. [Creating Your First Autonomous](#creating-your-first-autonomous)
4. [Common Movement Patterns](#common-movement-patterns)
5. [Advanced Techniques](#advanced-techniques)
6. [Troubleshooting](#troubleshooting)

---

## Understanding the Structure

### Key Files
- **`src/main.cpp`**: Main robot setup, motor configurations, and initialization
- **`src/autons.cpp`**: Your autonomous routines go here
- **`include/autons.hpp`**: Function declarations for your autonomous routines

### The Chassis Object
The `chassis` object controls all robot movement. It's defined in `main.cpp` and uses:
- Motor ports for left and right sides
- IMU (Inertial Measurement Unit) for heading/rotation tracking
- PID controllers for smooth, accurate movement

---

## Basic Movement Commands

### 1. Drive Forward/Backward

```cpp
// Drive forward 24 inches at DRIVE_SPEED
chassis.pid_drive_set(24_in, DRIVE_SPEED, true);
chassis.pid_wait();  // Wait until movement completes

// Drive backward 12 inches
chassis.pid_drive_set(-12_in, DRIVE_SPEED);
chassis.pid_wait();
```

**Parameters:**
- `24_in`: Distance in inches (use `-` for backward)
- `DRIVE_SPEED`: Speed (0-127)
- `true`: Enable slew (gradual acceleration - smoother movement)

### 2. Turn to an Angle

```cpp
// Turn to 90 degrees (absolute heading)
chassis.pid_turn_set(90_deg, TURN_SPEED);
chassis.pid_wait();

// Turn to 0 degrees (forward direction)
chassis.pid_turn_set(0_deg, TURN_SPEED);
chassis.pid_wait();
```

**Parameters:**
- `90_deg`: Target angle in degrees
- `TURN_SPEED`: Speed for turning (0-127)

### 3. Swing Turns (Pivot on One Side)

```cpp
// Lock left side, pivot right side to 45 degrees
chassis.pid_swing_set(ez::LEFT_SWING, 45_deg, SWING_SPEED, 45);
chassis.pid_wait();

// Lock right side, pivot left side to 0 degrees
chassis.pid_swing_set(ez::RIGHT_SWING, 0_deg, SWING_SPEED, 45);
chassis.pid_wait();
```

**When to use:** When you need to turn while maintaining your position more precisely, or when turning around an obstacle.

---

## Creating Your First Autonomous

### Step 1: Add Function Declaration

In `include/autons.hpp`, add:

```cpp
void my_first_auton();
```

### Step 2: Write Your Routine

In `src/autons.cpp`, write your function:

```cpp
void my_first_auton() {
  // Drive forward 24 inches
  chassis.pid_drive_set(24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  
  // Turn 90 degrees right
  chassis.pid_turn_set(90_deg, TURN_SPEED);
  chassis.pid_wait();
  
  // Drive forward 12 more inches
  chassis.pid_drive_set(12_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  
  // Turn back to starting direction
  chassis.pid_turn_set(0_deg, TURN_SPEED);
  chassis.pid_wait();
  
  // Drive back to start
  chassis.pid_drive_set(-24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
}
```

### Step 3: Add to Autonomous Selector

In `src/main.cpp`, in the `initialize()` function, add your auton to the list:

```cpp
ez::as::auton_selector.autons_add({
    {"Drive", drive_example},
    {"Turn", turn_example},
    {"My First Auton", my_first_auton},  // Add this line
    // ... other autons
});
```

### Step 4: Test Your Routine

1. Upload code to your robot
2. Select your autonomous from the brain screen menu
3. Run autonomous mode to test

---

## Common Movement Patterns

### Pattern 1: Drive and Turn Sequence

```cpp
void drive_and_turn_pattern() {
  // Drive forward
  chassis.pid_drive_set(36_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  
  // Turn 90 degrees
  chassis.pid_turn_set(90_deg, TURN_SPEED);
  chassis.pid_wait();
  
  // Drive more
  chassis.pid_drive_set(24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
}
```

### Pattern 2: Variable Speed During Movement

```cpp
void variable_speed_example() {
  // Start slow
  chassis.pid_drive_set(24_in, 30, true);
  
  // Speed up after moving 6 inches
  chassis.pid_wait_until(6_in);
  chassis.pid_speed_max_set(DRIVE_SPEED);
  
  // Wait for completion
  chassis.pid_wait();
}
```

### Pattern 3: Motion Chaining (Smoother Transitions)

```cpp
void smooth_motion() {
  chassis.pid_drive_set(24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  
  // Start turning before fully stopped (smoother)
  chassis.pid_turn_set(45_deg, TURN_SPEED);
  chassis.pid_wait_quick_chain();  // Starts next movement early
  
  chassis.pid_turn_set(-45_deg, TURN_SPEED);
  chassis.pid_wait_quick_chain();  // Chain again
  
  chassis.pid_turn_set(0_deg, TURN_SPEED);
  chassis.pid_wait();  // Final movement waits fully
}
```

### Pattern 4: Navigate to Coordinates

```cpp
void navigate_to_point() {
  // Navigate to coordinate (24, 36) inches at default speed
  navigate_to_coordinate(24.0, 36.0);
  
  // Navigate to coordinate at custom speed
  navigate_to_coordinate(48.0, 24.0, 100);
  
  // Navigate to coordinate and face specific heading (90 degrees)
  navigate_to_coordinate(36.0, 48.0, DRIVE_SPEED, 90.0);
}
```

**How it works:**
- Uses IMU for heading/rotation tracking
- Uses odometry (chassis tracking) for position
- Automatically calculates the path to the target coordinate
- Optionally sets a target heading when arriving at the coordinate

**Function Signatures:**
- `navigate_to_coordinate(target_x, target_y)` - Navigate with default speed
- `navigate_to_coordinate(target_x, target_y, speed)` - Navigate with custom speed
- `navigate_to_coordinate(target_x, target_y, speed, heading)` - Navigate with speed and target heading

See the `navigate_to_coordinate()` function in `autons.cpp` for implementation details.

---

## Advanced Techniques

### Handling Interference (Robot Gets Blocked)

```cpp
void robust_movement() {
  chassis.pid_drive_set(48_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  
  // Check if robot was blocked
  if (chassis.interfered) {
    // Back up a bit
    chassis.pid_drive_set(-6_in, 80);
    chassis.pid_wait();
    
    // Try again
    chassis.pid_drive_set(48_in, DRIVE_SPEED, true);
    chassis.pid_wait();
  }
}
```

### Getting Current Position

```cpp
void check_position() {
  // Get current robot position
  pose current_pos = chassis.odom_pose_get();
  
  // Print to console
  printf("Current X: %.2f, Y: %.2f, Theta: %.2f\n", 
         current_pos.x, current_pos.y, current_pos.theta);
  
  // Get current heading from IMU
  double heading = chassis.drive_imu_get();
  printf("Current heading: %.2f degrees\n", heading);
}
```

### Setting Starting Position

```cpp
void set_start_position() {
  // Set robot's starting position (useful for different starting locations)
  chassis.odom_xyt_set(0.0, 0.0, 0.0);  // X, Y, Theta in inches and degrees
}
```

---

## Coordinate Navigation Using IMU

The `navigate_to_coordinate()` function allows you to navigate your robot to specific X,Y coordinates on the field using IMU-based odometry tracking.

### Basic Usage

```cpp
void coordinate_navigation_example() {
  // Reset position to (0, 0, 0) at start
  chassis.odom_reset();
  chassis.drive_imu_reset();
  
  // Navigate to coordinate (24, 36) inches
  navigate_to_coordinate(24.0, 36.0);
  
  // Navigate to another point
  navigate_to_coordinate(48.0, 24.0, 100);  // Custom speed
  
  // Navigate to point and face specific direction (90 degrees)
  navigate_to_coordinate(36.0, 48.0, DRIVE_SPEED, 90.0);
}
```

### How It Works

1. **Current Position**: Gets the robot's current position using `chassis.odom_pose_get()`
2. **Target Calculation**: Calculates the path to the target coordinate
3. **Movement**: Uses `pid_odom_set()` to navigate smoothly to the target
4. **IMU Integration**: The IMU (port 7) tracks the robot's heading throughout the movement
5. **Odometry**: The chassis tracks X,Y position using encoder-based odometry

### Function Overloads

| Function Call | Description |
|--------------|-------------|
| `navigate_to_coordinate(x, y)` | Navigate with default speed (DRIVE_SPEED) |
| `navigate_to_coordinate(x, y, speed)` | Navigate with custom speed (0-127) |
| `navigate_to_coordinate(x, y, speed, heading)` | Navigate with speed and target heading (degrees) |

### Important Notes

- **Coordinate System**: Uses inches for X and Y coordinates
- **Starting Position**: Make sure to reset odometry (`chassis.odom_reset()`) at the start of autonomous if needed
- **Heading**: If you don't specify a target heading, the robot will navigate to the point without forcing a specific orientation
- **IMU Required**: This function relies on the IMU (connected to port 7) for accurate heading tracking
- **Odometry**: Position tracking uses the chassis's built-in odometry system

### Example: Field Navigation

```cpp
void field_navigation() {
  // Starting position
  chassis.odom_reset();
  chassis.drive_imu_reset();
  
  // Go to first goal
  navigate_to_coordinate(24.0, 36.0);
  // TODO: Perform action (intake, shoot, etc.)
  
  // Go to second goal
  navigate_to_coordinate(48.0, 48.0, 100);
  // TODO: Perform action
  
  // Return to starting position
  navigate_to_coordinate(0.0, 0.0);
  
  // Face starting direction
  chassis.pid_turn_set(0_deg, TURN_SPEED);
  chassis.pid_wait();
}
```

---

## Important Tips

### 1. Always Use `pid_wait()`
**❌ Bad:**
```cpp
chassis.pid_drive_set(24_in, DRIVE_SPEED);
chassis.pid_turn_set(90_deg, TURN_SPEED);  // Starts before drive finishes!
```

**✅ Good:**
```cpp
chassis.pid_drive_set(24_in, DRIVE_SPEED);
chassis.pid_wait();  // Wait for drive to finish
chassis.pid_turn_set(90_deg, TURN_SPEED);
chassis.pid_wait();  // Wait for turn to finish
```

### 2. Use Slew for Smooth Acceleration
Always use `true` for the slew parameter in `pid_drive_set()` to prevent wheel slip:
```cpp
chassis.pid_drive_set(24_in, DRIVE_SPEED, true);  // true = slew enabled
```

### 3. Tune Your PID Constants
In `default_constants()` function in `autons.cpp`, adjust:
- **Drive constants**: How quickly/smoothly robot drives
- **Turn constants**: How quickly/smoothly robot turns
- **Exit conditions**: When movement stops (time/distance thresholds)

### 4. Test in Practice Matches
- Run your autonomous multiple times
- Adjust distances and angles based on real-world results
- Use the PID tuner (press X in opcontrol when not in competition) to fine-tune

### 5. Use Units Properly
EZ-Template supports okapi units:
- `24_in` = 24 inches
- `90_deg` = 90 degrees
- `500_ms` = 500 milliseconds

Or use plain numbers:
- `24.0` = 24 inches
- `90.0` = 90 degrees

---

## Troubleshooting

### Robot Doesn't Stop Accurately
- **Problem:** Robot overshoots or undershoots target
- **Solution:** Adjust exit conditions in `default_constants()`:
  ```cpp
  chassis.pid_drive_exit_condition_set(90_ms, 1_in, 250_ms, 3_in, 500_ms, 500_ms);
  ```
  - Smaller error values = more precise stopping

### Robot Turns Wrong Direction
- **Problem:** Robot turns the long way around
- **Solution:** EZ-Template uses shortest path by default. Check your angle calculations.

### Robot Drifts While Driving
- **Problem:** Robot doesn't drive straight
- **Solution:** Increase heading PID constants in `default_constants()`:
  ```cpp
  chassis.pid_heading_constants_set(11.0, 0.0, 20.0);  // Increase P value
  ```

### IMU Not Working
- **Problem:** Robot doesn't know its heading
- **Solution:** 
  - Check IMU is connected to correct port (port 7 in your setup)
  - Wait for IMU to calibrate (controller will rumble when ready)
  - Check `chassis.drive_imu_calibrated()` returns true

### Movements Are Too Jerky
- **Problem:** Robot starts/stops too abruptly
- **Solution:** Enable slew and adjust slew constants:
  ```cpp
  chassis.slew_drive_constants_set(3_in, 70);  // Adjust ramp-up distance/speed
  ```

---

## Example: Complete Autonomous Routine

```cpp
void competition_auton() {
  // Drive to first goal (24 inches forward)
  chassis.pid_drive_set(24_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  
  // Turn to face goal
  chassis.pid_turn_set(45_deg, TURN_SPEED);
  chassis.pid_wait();
  
  // Drive closer to goal
  chassis.pid_drive_set(12_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  
  // TODO: Deploy mechanism here (intake, shooter, etc.)
  
  // Back up
  chassis.pid_drive_set(-12_in, DRIVE_SPEED, true);
  chassis.pid_wait();
  
  // Turn back to starting heading
  chassis.pid_turn_set(0_deg, TURN_SPEED);
  chassis.pid_wait();
  
  // Drive to next position
  chassis.pid_drive_set(36_in, DRIVE_SPEED, true);
  chassis.pid_wait();
}
```

---

## Quick Reference

### Movement Functions
| Function | Purpose |
|----------|---------|
| `pid_drive_set(distance, speed, slew)` | Drive forward/backward |
| `pid_turn_set(angle, speed)` | Turn to absolute angle |
| `pid_swing_set(side, angle, speed, angle)` | Pivot turn |
| `pid_odom_set(odom_movement)` | Navigate to coordinate (low-level) |
| `navigate_to_coordinate(x, y, speed, heading)` | Navigate to X,Y coordinate using IMU |
| `pid_wait()` | Wait for movement to complete |
| `pid_wait_until(distance)` | Wait until robot moves distance |
| `pid_wait_quick_chain()` | Wait but start next movement early |

### Information Functions
| Function | Purpose |
|----------|---------|
| `odom_pose_get()` | Get current position (x, y, theta) |
| `drive_imu_get()` | Get current heading in degrees |
| `drive_imu_calibrated()` | Check if IMU is ready |
| `interfered` | Check if robot was blocked |

### Setup Functions
| Function | Purpose |
|----------|---------|
| `odom_reset()` | Reset position to (0, 0, 0) |
| `odom_xyt_set(x, y, theta)` | Set starting position |
| `drive_imu_reset()` | Reset heading to 0 degrees |
| `odom_pose_get()` | Get current position (x, y, theta) |
| `drive_imu_get()` | Get current heading in degrees |

---

## Next Steps

1. **Practice**: Start with simple drive and turn routines
2. **Experiment**: Try different speeds and distances
3. **Tune**: Use PID tuner to optimize movements
4. **Test**: Run multiple times and adjust based on results
5. **Combine**: Add mechanisms (intake, shooter, etc.) to your routines

Happy coding! 🚀

