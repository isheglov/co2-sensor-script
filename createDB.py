import sqlite3

db_path = 'sensor_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    co2 INTEGER NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL
)
''')
conn.commit()
conn.close()
