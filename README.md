##CO2 Sensor Monitoring Script

This repository contains a Python script (co2v4.py) for monitoring CO2 levels, temperature, and humidity using a USB-zyTemp CO2 sensor connected to a Raspberry Pi. The script continuously reads data from the sensor and logs it to a CSV file for further analysis.

Features

	•	CO2 Monitoring: Reads CO2 levels (in ppm) from the sensor.
	•	Temperature Monitoring: Reads temperature data (in °C).
	•	Humidity Monitoring: Reads humidity data (in %).
	•	Data Logging: Appends the readings to a CSV file with timestamps.

Requirements

	•	Raspberry Pi (tested on Raspberry Pi Zero W)
	•	USB-zyTemp CO2 sensor (Holtek Semiconductor)
	•	Python 3.x
	•	Python packages:
	•	hidapi
	•	csv
	•	datetime

Setup and Installation

	1.	Clone the repository:
git clone https://github.com/yourusername/co2-sensor-script.git
cd co2-sensor-script
	2.	Set up your Python environment:
If you are using a virtual environment, create and activate it:
python3 -m venv myenv
source myenv/bin/activate
	3.	Install the required packages:
pip install hidapi
	4.	Connect the CO2 Sensor:
Ensure the USB-zyTemp CO2 sensor is connected to the Raspberry Pi.
	5.	Run the script:
python3 co2v4.py

Data Logging

The script logs data to a CSV file (co2_readings.csv). Each row contains the following information:

	•	Date and Time: When the reading was taken.
	•	CO2 Level (ppm): The CO2 concentration in parts per million.
	•	Temperature (°C): The temperature in degrees Celsius.
	•	Humidity (%): The humidity percentage.

Example of a CSV row:
2024-10-18 17:23:47;711;23.48;47.09

Running as a Background Service (Optional)

To continuously run the script in the background on a Raspberry Pi using systemd, follow these steps:

	1.	Create a systemd service file:
sudo nano /etc/systemd/system/co2sensor.service
	2.	Add the following content:
[Unit]
Description=CO2 Sensor Monitoring Service
After=network.target
[Service]
ExecStart=/home/pi/myenv/bin/python /home/pi/co2v4.py
WorkingDirectory=/home/pi/
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi
[Install]
WantedBy=multi-user.target
	3.	Enable and start the service:
sudo systemctl daemon-reload
sudo systemctl enable co2sensor.service
sudo systemctl start co2sensor.service

License

This project is licensed under the MIT License - see the LICENSE file for details.

Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

Contact

If you have any questions or issues, feel free to open an issue in the repository or contact me directly
