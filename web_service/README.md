# Web Service for Sensor Data Visualization

The web interface provides real-time data visualization and displays the current CO2, temperature, and humidity readings. Access it at [http://localhost:5000](http://localhost:5000) (or replace localhost with your Raspberry Pi's IP address if accessing from another device).

## Features

- **Real-time Data Visualization**: The main dashboard displays CO2 levels, temperature, and humidity over time.
- **Current Readings**: A dedicated page shows the latest sensor readings.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   Ensure that the `sensor_data.db` file is in the correct directory as specified in the application.

4. Run the application:
   ```bash
   python web_service/app.py
   ```

5. Access the web interface:
   Open your web browser and go to [http://localhost:5000](http://localhost:5000).

## Web Pages:

- **/**: Main dashboard for real-time data visualization.
- **/current**: Shows the latest sensor readings.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## Contact

If you have any questions or issues, feel free to open an issue in the repository or contact me directly.
