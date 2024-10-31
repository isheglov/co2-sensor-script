import RPi.GPIO as GPIO
import time
import sqlite3

# Configuration
DB_PATH = '../sensor_data.db'  # Path to your SQLite database
RELAY_PIN = 17  # GPIO pin connected to the relay (use the BCM numbering)
CO2_THRESHOLD_ON = 1100  # Turn relay on if CO2 exceeds this value
CO2_THRESHOLD_OFF = 900  # Turn relay off if CO2 falls below this value

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Start with the relay off

def get_last_co2_value(db_path):
    """Retrieve the most recent CO2 value from the database."""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query the last CO2 value from the sensor_data table
        cursor.execute("SELECT co2 FROM sensor_data ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        # Close the connection
        conn.close()

        # Return the CO2 value if available
        if result:
            return result[0]
        else:
            print("No data found in the database.")
            return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

try:
    while True:
        # Get the latest CO2 value from the database
        co2_value = get_last_co2_value(DB_PATH)
        
        if co2_value is not None:
            print(f"CO2 concentration: {co2_value} ppm")

            # Control the relay based on CO2 levels
            if co2_value > CO2_THRESHOLD_ON:
                GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn relay on
                print("Relay turned ON")
            elif co2_value < CO2_THRESHOLD_OFF:
                GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn relay off
                print("Relay turned OFF")
        
        # Wait for 5 seconds before checking again
        time.sleep(5)

except KeyboardInterrupt:
    print("Script interrupted by user")

finally:
    # Clean up GPIO settings
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn off relay on exit
    GPIO.cleanup()
    print("GPIO cleanup done")
