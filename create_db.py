# pylint: disable=C0114
# pylint: disable=import-error

import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv('DB_PATH')

conn = sqlite3.connect(DB_PATH)
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
