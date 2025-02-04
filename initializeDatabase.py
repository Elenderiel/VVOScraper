import sqlite3 as sql

conn = sql.connect('departureDatabase.db')

cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS main_table (
                Id TEXT PRIMARY KEY, 
                Network STRING,
                LineName INTEGER,
                ScheduledTime TEXT,
                Direction TEXT,
                Platform INTEGER,
                TransportationType TEXT,
                Occupancy STRNG,
                Status TEXT,
                RouteChanges INTEGER,
                CancelReasons STRING
                );"""
            )

cursor.execute("""CREATE TABLE IF NOT EXISTS delay_table (
               Id INTEGER PRIMARY KEY AUTOINCREMENT,
               MainId TEXT,
               TimeToDeparture TEXT,
               DelayTime INTEGER,
               FOREIGN KEY (MainId) REFERENCES main_table(Id) ON DELETE CASCADE
               );"""
            )

conn.commit()
conn.close()