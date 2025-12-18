# Gyroscope Testing Guide

## ✅ Code Uploaded Successfully!

Your code is now on the V5 Brain and will display gyroscope coordinates from **Port 10**.

## 📺 What You Should See on the Brain Screen

The Brain screen will display:
```
Gyroscope (Port 10):
X: [value] deg/s
Y: [value] deg/s
Z: [value] deg/s
```

## 🧪 How to Test the Gyroscope

### Test 1: Static Test (Robot Not Moving)
1. **Power on your V5 Brain** (if not already on)
2. **Look at the Brain screen**
3. **Expected Result:**
   - X, Y, Z values should be close to **0.00 deg/s** (or very small numbers)
   - Values may fluctuate slightly (±0.1 to ±0.5) due to sensor noise

### Test 2: Rotation Test (X-Axis - Roll)
1. **Hold the robot** in your hands
2. **Tilt the robot forward/backward** (like nodding)
3. **Expected Result:**
   - **X-axis value should change** (positive when tilting forward, negative when tilting back)
   - Values should range from about -100 to +100 deg/s depending on rotation speed

### Test 3: Rotation Test (Y-Axis - Pitch)
1. **Hold the robot** in your hands
2. **Tilt the robot left/right** (like shaking head "no")
3. **Expected Result:**
   - **Y-axis value should change** (positive when tilting right, negative when tilting left)
   - Values should range from about -100 to +100 deg/s

### Test 4: Rotation Test (Z-Axis - Yaw)
1. **Place the robot on a flat surface**
2. **Rotate the robot clockwise/counterclockwise** (spinning in place)
3. **Expected Result:**
   - **Z-axis value should change** (positive when rotating clockwise, negative counterclockwise)
   - Values should range from about -100 to +100 deg/s

### Test 5: Fast Movement Test
1. **Quickly rotate the robot** in any direction
2. **Expected Result:**
   - Values should **increase** (can reach 200-500+ deg/s for fast rotations)
   - When you stop, values should **return to near zero**

## ⚠️ Troubleshooting

### If you see "IMU Calibrating... Please wait"
- **Wait 2-3 seconds** - the IMU needs time to calibrate when first powered on
- The screen should update once calibration is complete

### If you see "Gyro Error Check Port 10"
- **Check the physical connection:**
  - Make sure the IMU/Gyroscope is plugged into **Port 10** on the Brain
  - Ensure the cable is securely connected
  - Try unplugging and replugging the sensor

### If values are always zero
- The sensor might not be calibrated yet - wait a few seconds
- Check if the sensor is properly connected to Port 10
- Make sure the sensor is a V5 Inertial Sensor (IMU)

### If values don't change when you move the robot
- Check that the sensor is securely mounted
- Verify the sensor is the correct type (V5 Inertial Sensor)
- Try restarting the Brain

## 📊 Understanding the Values

- **Units:** degrees per second (deg/s)
- **X-axis (Roll):** Forward/backward rotation
- **Y-axis (Pitch):** Left/right rotation  
- **Z-axis (Yaw):** Clockwise/counterclockwise rotation
- **At rest:** Values should be near 0 (±0.5 deg/s is normal)
- **During rotation:** Values increase proportionally to rotation speed

## 🎯 Quick Test Checklist

- [ ] Brain screen shows "Gyroscope (Port 10):" with X, Y, Z values
- [ ] Values are near zero when robot is still
- [ ] X-axis changes when tilting forward/backward
- [ ] Y-axis changes when tilting left/right
- [ ] Z-axis changes when rotating clockwise/counterclockwise
- [ ] Values return to near zero when movement stops

## 💡 Tips

- The values update in **real-time** on the Brain screen
- You can see the values change as you move the robot
- The sensor is most accurate when the robot is moving smoothly
- Fast, jerky movements may show higher values

