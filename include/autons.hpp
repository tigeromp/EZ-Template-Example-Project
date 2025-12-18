#pragma once

void default_constants();
void drive_example();
void turn_example();
void drive_and_turn();
void wait_until_change_speed();
void swing_example();
void motion_chaining();
void combining_movements();
void interfered_example();

// Navigate to coordinate functions
void navigate_to_coordinate(double target_x, double target_y, int speed, double target_heading);
void navigate_to_coordinate(double target_x, double target_y);
void navigate_to_coordinate(double target_x, double target_y, int speed);
void navigate_to_coordinates_example();