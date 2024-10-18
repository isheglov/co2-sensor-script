import os
import hid
import time
import csv
from datetime import datetime

# Path to your USB-zyTemp CO2 sensor
device_path = b'/dev/hidraw0'

# CSV file path
csv_file_path = 'co2_readings.csv'

# Variables to store the most recent readings
current_co2 = None
current_temperature = None
current_humidity = None

# Check if the CSV file already exists (to prevent rewriting the header)
file_exists = os.path.isfile(csv_file_path)

def save_to_csv():
    # Get the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Open the CSV file in append mode and write the data
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        # Write the header if the file is new
        if not file_exists:
            writer.writerow(['date', 'co2', 'temperature', 'humidity'])

        # Round temperature and humidity to two decimal places before writing
        writer.writerow([current_time, current_co2, round(current_temperature, 2), round(current_humidity, 2)])

    print(f"Data saved: {current_time}; {current_co2}; {round(current_temperature, 2)}; {round(current_humidity, 2)}")

def parse_data(data):
    global current_co2, current_temperature, current_humidity

    if not data:
        return

    metric = data[0]
    value_high = data[1]
    value_low = data[2]
    checksum = data[3]
    r4 = data[4]

    # Combine high and low bytes into the final value
    value = (value_high << 8) + value_low

    if r4 != 0x0D:  # Ensure that the terminator byte is correct
        print("Invalid data received.")
        return

    # Process the metric type
    if metric == 0x50:  # CO2 reading (0x50 = 80 in decimal)
        current_co2 = value
        print(f"CO2 Level: {current_co2} ppm")
    elif metric == 0x42:  # Temperature reading (0x42 = 66 in decimal)
        current_temperature = (value / 16.0) - 273.15
        print(f"Temperature: {current_temperature:.2f} °C")
    elif metric == 0x41:  # Humidity reading (0x41 = 65 in decimal)
        current_humidity = value / 100.0  # Assuming humidity is reported in hundredths of a percent
        print(f"Humidity: {current_humidity:.2f}%")
    else:
        print(f"Unknown metric: {metric}, value: {value}")

    # If all three values (CO2, Temperature, Humidity) have been updated, save them to the CSV file
    if current_co2 is not None and current_temperature is not None and current_humidity is not None:
        save_to_csv()

try:
    print("Opening the device...")
    h = hid.device()
    h.open_path(device_path)  # Open the device by its path

    # Send a basic feature report to initialize the device
    report = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
    h.send_feature_report(bytearray(report))

    # Continuously read data every 5 seconds
    while True:
        data = h.read(8, timeout_ms=5000)  # Timeout after 5 seconds if no data is received
        if data:
            print(f"Data read: {data}")
            parse_data(data)
        else:
            print("No data received from the device.")

        time.sleep(5)  # Wait for 5 seconds before reading again

    h.close()
except IOError as ex:
    print(f"Error: {ex}")
    print("Failed to open or communicate with the device.")
finally:
    print("Done")
