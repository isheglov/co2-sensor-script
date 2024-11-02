import pandas as pd
from flask import Flask, render_template
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import sqlite3

app = Flask(__name__)

DB_NAME = '../sensor_data.db'

def get_latest_data():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Fetch the latest data
        cursor.execute("SELECT date, co2, temperature, humidity FROM sensor_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            return {
                'date': row[0],
                'co2': int(row[1]),
                'temperature': round(row[2],2),
                'humidity': float(row[3])
            }
        else:
            return {
                'date': 'N/A',
                'co2': 'N/A',
                'temperature': 'N/A',
                'humidity': 'N/A'
            }
    except Exception as e:
        print(f"Error reading the latest data: {e}")
        return {
            'date': 'Error',
            'co2': 'Error',
            'temperature': 'Error',
            'humidity': 'Error'
        }
    finally:
        conn.close()


def fetch_data_from_db():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT date, co2, temperature, humidity FROM sensor_data"
        df = pd.read_sql_query(query, conn)
        
        # Convert 'date' column to datetime
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error reading from database: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    finally:
        conn.close()

@app.route('/')
def index():
    # Fetch data from the database
    df = fetch_data_from_db()

    # Check if the DataFrame is empty
    if df.empty:
        return render_template('index.html', graph_html="No data available.")

    # Create a plotly figure with 3 rows for CO2, temperature, and humidity
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("CO₂ Levels Over Time", "Temperature Over Time", "Humidity Over Time"))

    # Add CO2 data over time
    fig.add_trace(go.Scatter(x=df['date'], y=df['co2'], mode='lines', name='CO₂ over time'), row=1, col=1)

    fig.add_trace(go.Scatter(x=df['date'], y=df['temperature'], mode='lines', name='Temperature (°C)'), row=2, col=1)

    fig.add_trace(go.Scatter(x=df['date'], y=df['humidity'], mode='lines', name='Humidity (%)'), row=3, col=1)

    # Add titles and labels
    fig.update_layout(title='Sensor Data Over Time',
                      xaxis_title='Time',
                      height=800)  # Adjust height for better visibility

    # Convert the figure to an HTML div string
    graph_html = fig.to_html(full_html=False)

    # Render template with the graph
    return render_template('index.html', graph_html=graph_html)
        
@app.route('/current')
def current():
    current_data = get_latest_data()
    return render_template('current.html', current_data=current_data)
        
@app.route('/deploy_test')
def deploy_test():
    return render_template('deploy_test.html', number=2)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
