# pylint: disable=C0114
# pylint: disable=import-error

import sqlite3

DB_PATH = 'sensor_data.db'

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
