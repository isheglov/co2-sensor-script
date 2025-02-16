"""
Monitor Module

This script monitors CO2 levels from a SQLite database and controls a relay
connected to a Raspberry Pi GPIO pin based on predefined CO2 thresholds.
The relay is used to activate or deactivate a device (e.g., ventilation system)
to maintain safe CO2 concentrations.

When the CO2 level exceeds the upper threshold, the fan is turned on for 5 minutes
to reduce the CO2 concentration. After 5 minutes, the fan is automatically turned off.
"""

# pylint: disable=import-error

import time
import os
import sqlite3
from RPi import GPIO
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_PATH = os.getenv('DB_PATH')
RELAY_PIN = 17  # GPIO pin connected to the relay (use the BCM numbering)
CO2_THRESHOLD_ON = 800  # CO2 ppm level to turn relay on
FAN_DURATION = 300  # Duration to keep the fan on (in seconds)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

def get_last_co2_value(db_path):
    """Retrieve the most recent CO2 value from the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT co2 FROM sensor_data ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        conn.close()

        if result:
            return result[0]

        print("No data found in the database.")
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def activate_fan():
    """Activate the fan by turning the relay on."""
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    print("Relay turned ON - Fan activated.")

def deactivate_fan():
    """Deactivate the fan by turning the relay off."""
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("Relay turned OFF - Fan deactivated.")

def main():
    """Main loop to monitor CO2 levels and control the fan."""
    fan_active = False
    fan_start_time = None

    try:
        while True:
            co2_value = get_last_co2_value(DB_PATH)

            if co2_value is not None:
                print(f"CO2 concentration: {co2_value} ppm")

                current_time = time.time()

                if not fan_active:
                    if co2_value > CO2_THRESHOLD_ON:
                        activate_fan()
                        fan_active = True
                        fan_start_time = current_time
                else:
                    if current_time - fan_start_time >= FAN_DURATION:
                        deactivate_fan()
                        print("Pausing fan for 5 minutes.")
                        time.sleep(300)
                        print("Resuming monitoring after pause.")
                        fan_active = False
                        fan_start_time = None
                    else:
                        remaining_time = int(FAN_DURATION - (current_time - fan_start_time))
                        print(
                            f"Fan is active. Time remaining: {remaining_time} seconds."
                        )

            time.sleep(5)

    except KeyboardInterrupt:
        print("Script interrupted by user")

    finally:
        if fan_active:
            deactivate_fan()
        GPIO.cleanup()
        print("GPIO cleanup done")

if __name__ == '__main__':
    main()
