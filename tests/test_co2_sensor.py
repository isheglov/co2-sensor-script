"""
Unit tests for the CO2Sensor class.
"""

import os
import sys
import sqlite3
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to the path to import CO2Sensor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from co2_sensor import CO2Sensor  # pylint: disable=wrong-import-position


class TestCO2Sensor(unittest.TestCase):
    """Tests for the CO2Sensor class."""

    def setUp(self):
        """Set up the test environment."""
        self.test_db_path = "test_sensor_data.db"
        self.device_path = b'/dev/hidraw0'

        # Create a test database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            co2 INTEGER NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS last_day_sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            co2 INTEGER NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        );
        ''')
        conn.commit()
        conn.close()

        # Create CO2Sensor instance
        self.sensor = CO2Sensor(self.device_path, self.test_db_path)

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_init(self):
        """Test the initialization of the CO2Sensor class."""
        self.assertEqual(self.sensor.device_path, self.device_path)
        self.assertEqual(self.sensor.db_path, self.test_db_path)
        self.assertIsNone(self.sensor.current_co2)
        self.assertIsNone(self.sensor.current_temperature)
        self.assertIsNone(self.sensor.current_humidity)
        self.assertIsNone(self.sensor.h)

    def test_parse_data_co2(self):
        """Test parsing CO2 data."""
        # CO2 data: metric=0x50, value_high=0x02, value_low=0x58, r4=0x0D
        # This should result in a CO2 value of (0x02 << 8) + 0x58 = 512 + 88 = 600 ppm
        sensor_data = [0x50, 0x02, 0x58, 0x00, 0x0D, 0x00, 0x00, 0x00]
        self.sensor.parse_data(sensor_data)

        self.assertEqual(self.sensor.current_co2, 600)
        self.assertIsNone(self.sensor.current_temperature)
        self.assertIsNone(self.sensor.current_humidity)

    def test_parse_data_temperature(self):
        """Test parsing temperature data."""
        # Temperature data: metric=0x42, value_high=0x11, value_low=0x00, r4=0x0D
        # Value: (0x11 << 8) + 0x00 = 4352
        # Temperature calculation: (4352 / 16.0) - 273.15 = 272 - 273.15 = -1.15°C
        sensor_data = [0x42, 0x11, 0x00, 0x00, 0x0D, 0x00, 0x00, 0x00]
        self.sensor.parse_data(sensor_data)

        self.assertIsNone(self.sensor.current_co2)
        self.assertAlmostEqual(self.sensor.current_temperature, -1.15, places=2)
        self.assertIsNone(self.sensor.current_humidity)

    def test_parse_data_humidity(self):
        """Test parsing humidity data."""
        # Humidity data: metric=0x41, value_high=0x13, value_low=0x88, r4=0x0D
        # Value: (0x13 << 8) + 0x88 = 4904
        # Humidity calculation: 4904 / 100.0 = 49.04% (rounded to 50.0% in the code)
        sensor_data = [0x41, 0x13, 0x88, 0x00, 0x0D, 0x00, 0x00, 0x00]
        self.sensor.parse_data(sensor_data)

        self.assertIsNone(self.sensor.current_co2)
        self.assertIsNone(self.sensor.current_temperature)
        self.assertAlmostEqual(self.sensor.current_humidity, 50.0, places=2)

    def test_parse_data_invalid_terminator(self):
        """Test parsing data with invalid terminator byte."""
        # Data with invalid terminator (r4 != 0x0D)
        sensor_data = [0x50, 0x02, 0x58, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.sensor.parse_data(sensor_data)

        # Values should remain unchanged
        self.assertIsNone(self.sensor.current_co2)
        self.assertIsNone(self.sensor.current_temperature)
        self.assertIsNone(self.sensor.current_humidity)

    def test_parse_data_unknown_metric(self):
        """Test parsing data with unknown metric."""
        # Data with unknown metric (not 0x50, 0x42, or 0x41)
        sensor_data = [0x30, 0x02, 0x58, 0x00, 0x0D, 0x00, 0x00, 0x00]
        self.sensor.parse_data(sensor_data)

        # Values should remain unchanged
        self.assertIsNone(self.sensor.current_co2)
        self.assertIsNone(self.sensor.current_temperature)
        self.assertIsNone(self.sensor.current_humidity)

    def test_parse_data_empty(self):
        """Test parsing empty data."""
        self.sensor.parse_data([])

        # Values should remain unchanged
        self.assertIsNone(self.sensor.current_co2)
        self.assertIsNone(self.sensor.current_temperature)
        self.assertIsNone(self.sensor.current_humidity)

    @patch('sqlite3.connect')
    @patch('datetime.datetime')
    def test_save_to_db(self, mock_datetime, mock_connect):
        """Test saving data to the database."""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-03-16 12:00:00"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Set sensor values
        self.sensor.current_co2 = 800
        self.sensor.current_temperature = 22.5
        self.sensor.current_humidity = 45.0

        # Call save_to_db
        self.sensor.save_to_db()

        # Verify database operations
        mock_connect.assert_called_once_with(self.test_db_path)
        self.assertEqual(mock_cursor.execute.call_count, 3)

        # Verify that execute was called with correct SQL patterns
        calls = mock_cursor.execute.call_args_list
        self.assertTrue(any('INSERT INTO sensor_data' in str(call) for call in calls))
        self.assertTrue(any('INSERT INTO last_day_sensor_data' in str(call) for call in calls))
        self.assertTrue(any('DELETE FROM last_day_sensor_data' in str(call) for call in calls))

        # Check commit and close
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('sqlite3.connect')
    def test_save_to_db_error(self, mock_connect):
        """Test handling database errors."""
        # Setup mocks to raise exception
        mock_connect.side_effect = sqlite3.Error("Test DB error")

        # Set sensor values
        self.sensor.current_co2 = 800
        self.sensor.current_temperature = 22.5
        self.sensor.current_humidity = 45.0

        # Call save_to_db (should not raise an exception)
        self.sensor.save_to_db()

        # Verify connect was called
        mock_connect.assert_called_once_with(self.test_db_path)

    @patch('hid.device')
    def test_run_ioerror(self, mock_hid_device):
        """Test handling IOError when opening device."""
        # Setup mock to raise IOError
        mock_device = MagicMock()
        mock_hid_device.return_value = mock_device
        mock_device.open_path.side_effect = IOError("Test IO error")

        # Call run method
        self.sensor.run()

        # Verify hid.device was instantiated and open_path was called
        mock_hid_device.assert_called_once()
        mock_device.open_path.assert_called_once_with(self.device_path)
        mock_device.close.assert_called_once()

    @patch('co2_sensor.CO2Sensor.parse_data')
    @patch('hid.device')
    @patch('time.sleep')
    def test_run_read_data_success(self, mock_sleep, mock_hid_device, mock_parse_data):
        """Test successful data reading."""
        # Setup mock for successful read
        mock_device = MagicMock()
        mock_hid_device.return_value = mock_device

        # Make run exit by raising an exception on the first sleep
        mock_sleep.side_effect = KeyboardInterrupt()

        # Mock device.read to return data
        test_data = [0x50, 0x02, 0x58, 0x00, 0x0D, 0x00, 0x00, 0x00]
        mock_device.read.return_value = test_data

        # Call run method (will exit due to KeyboardInterrupt on sleep)
        try:
            self.sensor.run()
        except KeyboardInterrupt:
            pass

        # Verify device operations
        mock_hid_device.assert_called_once()
        mock_device.open_path.assert_called_once_with(self.device_path)
        mock_device.send_feature_report.assert_called_once()
        mock_device.read.assert_called_once_with(8, timeout_ms=10000)

        # Verify parse_data was called with the test data
        mock_parse_data.assert_called_once_with(test_data)


if __name__ == '__main__':
    unittest.main()
