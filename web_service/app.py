# pylint: disable=C0114
# pylint: disable=import-error

import sqlite3
import pandas as pd
from flask import Flask, render_template
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from werkzeug.middleware.profiler import ProfilerMiddleware

app = Flask(__name__)

DB_NAME = '../sensor_data.db'

def get_latest_data():
    """
    Retrieve the latest sensor data from the SQLite database.

    Returns:
        dict: A dictionary containing the latest date, CO2, temperature, and humidity.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Fetch the latest data
        cursor.execute(
            "SELECT date, co2, temperature, humidity FROM last_day_sensor_data ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()

        if row:
            return {
                'date': row[0],
                'co2': int(row[1]),
                'temperature': round(row[2], 2),
                'humidity': float(row[3])
            }

        return {
            'date': 'N/A',
            'co2': 'N/A',
            'temperature': 'N/A',
            'humidity': 'N/A'
        }
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {
            'date': 'Error',
            'co2': 'Error',
            'temperature': 'Error',
            'humidity': 'Error'
        }
    finally:
        conn.close()

def fetch_last_day():
    """
    Fetch last 24 hours sensor data from the SQLite database.

    Returns:
        pandas.DataFrame: A DataFrame containing all sensor data.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT date, co2, temperature, humidity FROM last_day_sensor_data;"
        df = pd.read_sql_query(query, conn)

        # Convert 'date' column to datetime
        df['date'] = pd.to_datetime(df['date'])
        return df
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    finally:
        conn.close()

@app.route('/')
def index():
    """
    Render the main dashboard with sensor data graphs.

    Returns:
        str: Rendered HTML template.
    """
    # Fetch data from the database
    df = fetch_last_day()

    # Check if the DataFrame is empty
    if df.empty:
        return render_template('index.html', graph_html="No data available.")

    # Create a plotly figure with 3 rows for CO2, temperature, and humidity
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        subplot_titles=(
            "CO₂ Levels Over Time",
            "Temperature Over Time",
            "Humidity Over Time"
        )
    )

    # Add CO2 data over time
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['co2'], mode='lines', name='CO₂ over time'),
        row=1,
        col=1
    )

    # Add Temperature data over time
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['temperature'], mode='lines', name='Temperature (°C)'),
        row=2,
        col=1
    )

    # Add Humidity data over time
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['humidity'], mode='lines', name='Humidity (%)'),
        row=3,
        col=1
    )

    # Add titles and labels
    fig.update_layout(
        title='Sensor Data Over Time',
        xaxis_title='Time',
        height=800  # Adjust height for better visibility
    )

    # Convert the figure to an HTML div string
    graph_html = fig.to_html(full_html=False)

    # Render template with the graph
    return render_template('index.html', graph_html=graph_html)

@app.route('/current')
def current():
    """
    Render the current sensor data.

    Returns:
        str: Rendered HTML template.
    """
    current_data = get_latest_data()
    return render_template('current.html', current_data=current_data)

if __name__ == '__main__':
    app.debug = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30]) # Show only top 30 slowest functions
    app.run(host='0.0.0.0', port=5000)
