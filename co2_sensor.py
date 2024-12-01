# pylint: disable=C0114
# pylint: disable=import-error

import time
import sqlite3
from datetime import datetime
import hid

# Path to your USB-zyTemp CO2 sensor
DEVICE_PATH = b'/dev/hidraw0'

# Path to the SQLite database
DB_PATH = 'sensor_data.db'


class CO2Sensor:
    """
    CO2Sensor handles communication with the USB-zyTemp CO2 sensor,
    parses incoming data, and stores sensor readings in a SQLite database.

    Attributes:
        device_path (bytes): The path to the HID device.
        db_path (str): The file path to the SQLite database.
        current_co2 (int or None): The latest CO2 concentration in ppm.
        current_temperature (float or None): The latest temperature reading in °C.
        current_humidity (float or None): The latest humidity percentage.
        h (hid.device or None): The HID device instance for communication.
    """

    def __init__(self, device_path, db_path):
        self.device_path = device_path
        self.db_path = db_path
        self.current_co2 = None
        self.current_temperature = None
        self.current_humidity = None
        self.h = None

    def save_to_db(self):
        """
        Save the current CO2, temperature, and humidity readings to the SQLite database.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO sensor_data (date, co2, temperature, humidity)
                VALUES (?, ?, ?, ?)
            """, (current_time, self.current_co2, self.current_temperature, self.current_humidity))

            cursor.execute("""
                INSERT INTO last_day_sensor_data (date, co2, temperature, humidity)
                VALUES (?, ?, ?, ?)
            """, (current_time, self.current_co2, self.current_temperature, self.current_humidity))
            
            cursor.execute("""
                DELETE FROM last_day_sensor_data WHERE date < datetime('now', '-24 hours')
            """)

            conn.commit()
            conn.close()

            print(
                f"Data saved to database: {current_time}; "
                f"CO2: {self.current_co2} ppm; "
                f"Temperature: {self.current_temperature:.2f} °C; "
                f"Humidity: {self.current_humidity:.2f}%"
            )
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def parse_data(self, sensor_data):
        """
        Parse and handle incoming data from the CO2 sensor.

        Args:
            sensor_data (list[int]): A list of integers 
            representing the raw data bytes from the sensor.
        """
        if not sensor_data:
            return

        metric = sensor_data[0]
        value_high = sensor_data[1]
        value_low = sensor_data[2]
        r4 = sensor_data[4]

        # Combine high and low bytes into the final value
        value = (value_high << 8) + value_low

        if r4 != 0x0D:  # Ensure that the terminator byte is correct
            print("Invalid data received.")
            return

        # Process the metric type
        if metric == 0x50:  # CO2 reading (0x50 = 80 in decimal)
            self.current_co2 = value
            print(f"CO2 Level: {self.current_co2} ppm")
        elif metric == 0x42:  # Temperature reading (0x42 = 66 in decimal)
            self.current_temperature = (value / 16.0) - 273.15
            print(f"Temperature: {self.current_temperature:.2f} °C")
        elif metric == 0x41:  # Humidity reading (0x41 = 65 in decimal)
            self.current_humidity = value / 100.0
            # Assuming humidity is reported in hundredths of a percent
            print(f"Humidity: {self.current_humidity:.2f}%")
        else:
            print(f"Unknown metric: {metric}, value: {value}")

        # If all three values (CO2, Temperature, Humidity)
        # have been updated, save them to the database
        if (
            self.current_co2 is not None
            and self.current_temperature is not None
            and self.current_humidity is not None
        ):
            self.save_to_db()

    def run(self):
        """
        Initialize the device and start reading data.
        """
        try:
            print("Opening the device...")
            self.h = hid.device()
            self.h.open_path(self.device_path)  # Open the device by its path

            # Send a basic feature report to initialize the device
            report = [
                0xc4, 0xc6, 0xc0, 0x92,
                0x40, 0x23, 0xdc, 0x96
            ]
            self.h.send_feature_report(bytearray(report))

            while True:
                data = self.h.read(8, timeout_ms=10000)
                if data:
                    print(f"Data read: {data}")
                    self.parse_data(data)
                else:
                    print("No data received from the device.")
                time.sleep(10) 

            self.h.close()
        except IOError as ex:
            print(f"Error: {ex}")
            print("Failed to open or communicate with the device.")
        finally:
            if self.h:
                self.h.close()
            print("Done")


if __name__ == "__main__":
    sensor = CO2Sensor(DEVICE_PATH, DB_PATH)
    sensor.run()
