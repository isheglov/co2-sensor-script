import RPi.GPIO as GPIO
import time

# Configuration
FILE_PATH = '../co2_readings.csv'
RELAY_PIN = 17  # GPIO pin connected to the relay (use the BCM numbering)
CO2_THRESHOLD_ON = 1100  # Turn relay on if CO2 exceeds this value
CO2_THRESHOLD_OFF = 900  # Turn relay off if CO2 falls below this value

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Start with the relay off

def get_last_line(file_path):
    """Read the last line from a file."""
    with open(file_path, 'rb') as f:
        f.seek(-2, 2)  # Move to the end of the file
        while f.read(1) != b'\n':  # Skip backward to the start of the last line
            f.seek(-2, 1)
        last_line = f.readline().decode()  # Decode the last line
    return last_line.strip()

def extract_co2_value(line):
    """Extract the CO2 value from a line in the format 'timestamp;co2;temp;humidity'."""
    try:
        parts = line.split(';')
        co2_value = int(parts[1])  # Second value is the CO2 concentration
        return co2_value
    except (IndexError, ValueError) as e:
        print(f"Error parsing line '{line}': {e}")
        return None

try:
    while True:
        # Read the last line and extract the CO2 value
        last_line = get_last_line(FILE_PATH)
        co2_value = extract_co2_value(last_line)
        
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
