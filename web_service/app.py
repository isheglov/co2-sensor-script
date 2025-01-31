# pylint: disable=C0114
# pylint: disable=import-error

import os
import sqlite3
import pandas as pd
from flask import Flask, render_template
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from werkzeug.middleware.profiler import ProfilerMiddleware

app = Flask(__name__)

# Determine the absolute path to the database file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, 'sensor_data.db')

def get_latest_data():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
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
        return {'date': 'N/A', 'co2': 'N/A', 'temperature': 'N/A', 'humidity': 'N/A'}
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {'date': 'Error', 'co2': 'Error', 'temperature': 'Error', 'humidity': 'Error'}
    finally:
        conn.close()

def fetch_last_day():
    try:
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT date, co2, temperature, humidity FROM last_day_sensor_data;"
        df = pd.read_sql_query(query, conn)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def resample_data(df, rule='1T'):
    """
    Resample the data to a specified time interval.
    
    Args:
        df (pd.DataFrame): The original DataFrame with sensor data.
        rule (str): Resampling frequency (e.g., '1T' for 1 minute).
    
    Returns:
        pd.DataFrame: A DataFrame with resampled data.
    """
    # Ensure that 'date' is set as the index
    if df.index.name != 'date':
        df = df.set_index('date')
    resampled_df = df.resample(rule).mean()
    resampled_df.reset_index(inplace=True)
    return resampled_df

@app.route('/')
def index():
    df_orig = fetch_last_day()
    if df_orig.empty:
        return render_template('index.html', graph_html="No data available.")
    
    # Resample data to one-minute intervals to reduce the number of points
    df = resample_data(df_orig, rule='1T')

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("CO₂ Levels Over Time", "Temperature Over Time", "Humidity Over Time")
    )
    fig.add_trace(go.Scatter(x=df['date'], y=df['co2'], mode='lines', name='CO₂ over time'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['temperature'], mode='lines', name='Temperature (°C)'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['humidity'], mode='lines', name='Humidity (%)'), row=3, col=1)
    fig.update_layout(title='Sensor Data Over Time', xaxis_title='Time', height=800)
    graph_html = fig.to_html(full_html=False)
    return render_template('index.html', graph_html=graph_html)

@app.route('/current')
def current():
    current_data = get_latest_data()
    return render_template('current.html', current_data=current_data)

if __name__ == '__main__':
    app.debug = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.run(host='0.0.0.0', port=5000)
