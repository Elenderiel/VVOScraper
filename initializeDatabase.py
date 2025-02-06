import sqlite3 as sql

conn = sql.connect('departureDatabase.db')

cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS main_table (
                Id TEXT PRIMARY KEY,
                LineId, 
                Network TEXT,
                LineName INTEGER,
                ScheduledTime INTEGER,
                Direction TEXT,
                Platform INTEGER,
                TransportationType TEXT,
                Occupancy TEXT,
                Status TEXT,
                RouteChanges INTEGER,
                CancelReasons TEXT
                );"""
            )

cursor.execute("""CREATE TABLE IF NOT EXISTS delay_table (
               Id INTEGER PRIMARY KEY AUTOINCREMENT,
               MainId TEXT,
               TimeStamp INTEGER,
               DelayTime INTEGER, 
               FOREIGN KEY (MainId) REFERENCES main_table(Id) ON DELETE CASCADE
               );"""
            )

conn.commit()
print('\033[92m' + 'database initialized' + '\033[0m')
conn.close()