# MAVLink communication with H743 W-Lite using pymavlink
from pymavlink import mavutil
import time

# Connect to the FC via serial (adjust tty and baudrate as needed)
master = mavutil.mavlink_connection('/dev/ttyAMA0', baud=57600)
master.wait_heartbeat()
print("Connected to flight controller.")

# Function to command a servo to release payload (e.g., channel 8)
def drop_payload():
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0,      # confirmation
        8,      # servo number (e.g., channel 8)
        1100,   # PWM value to release
        0, 0, 0, 0, 0
    )
    print("Payload drop signal sent.")

# Call drop_payload() when ready in your detection logic