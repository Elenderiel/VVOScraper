import requests
import schedule
import os.path
from time import mktime, sleep

import sqlite3 as sql
from schedule import repeat, every
from datetime import datetime, timezone, time


url = 'https://webapi.vvo-online.de/dm'
numberOfDepartures = 3
intervalInMin = 1

params = {
    'stopid' : 33000784,
    'limit' : numberOfDepartures,
}

#connecting with the database or exiting, if database not initialized
if os.path.exists('departureDatabase.db'):
    conn = sql.connect('departureDatabase.db')
    cursor = conn.cursor()
else:
    exit('\033[91m' + 'please run "initializeDatabase.py" first to make sure the database is initialized correctly' + '\033[0m')


#inserting the data into the primary and secondary table
def insertIntoDatabase(date, data):
    try:
        obj = Departure(**data)
        cursor.execute("""INSERT OR IGNORE INTO main_table (Id, LineId, Network, LineName, ScheduledTime, Direction, Platform, TransportationType, Occupancy, Status, RouteChanges, CancelReasons)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, (obj.id, obj.lineId, obj.network, obj.name, obj.scheduledTime, obj.direction, obj.platform, obj.transportationType, obj.occupancy, obj.status, obj.routeChanges, obj.cancelReasons)
                       )
    
        cursor.execute("""INSERT INTO delay_table (MainId, TimeStamp, DelayTime)
                       VALUES (?, ?, ?)""", (obj.id, obj.timestamp, obj.delayTime)
                       )
        conn.commit()
    except Exception as e:
        print(f'{date} ... ' + '\033[91m' + 'an exception occured while inserting values into database: ' + '\033[0m' + f'{e}')


#extracting and formating data from response.json() object
def extractData(timestamp, date, departures):
    try:
        for departure in departures:
            data = {
                'network' : departure['Diva']['Network'], 
                'name' : departure['LineName'], 
                'scheduledTime' : int(departure['ScheduledTime'][6:-10]),
                'direction' : departure['Direction'],
                'platform' : int(departure['Platform']['Name']),
                'transportationType' : departure['Mot'],
                'occupancy' : departure['Occupancy'], 
                'status' : 'Unknown',
                'routeChanges' : int(bool(departure['RouteChanges'])), 
                'cancelReasons' : ';'.join(departure['CancelReasons']),
                'timestamp' : timestamp,
                'realTime' : int(departure['ScheduledTime'][6:-10])
            }

            #additional checks for information that are not available for every departure
            if 'State' in departure: 
                data['status'] = departure['State']
            if 'RealTime' in departure:
                data['realTime'] = int(departure['RealTime'][6:-10])

            insertIntoDatabase(date, data)
    except Exception as e:
        print(f'{date} ... ' + '\033[91m' + 'an exception occured while exctracting information from response: ' + '\033[0m' + f'{e}')


#class to store information in an instance before inserting it into a database, to later be able to add features more easily
class Departure:

    def __init__(self, network:str, name:str, scheduledTime:int, direction:str, platform:int, transportationType:str, occupancy:str, status:str, routeChanges:int, cancelReasons:str, timestamp:int, realTime:int):
        self.id = name + '|' + str(scheduledTime) + '|' + direction
        self.lineId = name + '|' + direction
        self.network = network
        self.name = name
        self.scheduledTime = scheduledTime
        self.direction = direction
        self.platform = platform
        self.transportationType = transportationType
        self.occupancy = occupancy
        self.status = status
        self.routeChanges = routeChanges
        self.cancelReasons = cancelReasons
        self.timestamp = timestamp
        self.delayTime = (realTime - scheduledTime) // 60
    
    def formatTime(self, time:str) -> int:
        time = int(time[:-8])
        return datetime.fromtimestamp(time)


#schedule loop to fetch upcoming departure information from vvo api until time limit is met
@repeat(every(intervalInMin).minutes.until(time(15, 32, 0)))
def getDepartures():
    timestamp = (int(mktime(datetime.now(timezone.utc).timetuple())) // 60 * 60) + 3600 #timestamp of request to determine time difference to scheduled time
    date = datetime.fromtimestamp(timestamp)
    try:
        request = requests.get(url=url, params=params)
        status = request.status_code
        if status == 200:
            response = request.json()
            departures = response['Departures']
            print(f'{date} ... request successful: ' + '\033[92m' + f'{status}' + '\033[0m')
            extractData(timestamp, date, departures)
        else:
            print(f'{date} ... ' + '\033[91m' + f'request failed with error code: {status}' + '\033[0m')
    except Exception as e:
        print(f'{date} ... ' + '\033[91m' + 'an exception occured while fetching: ' + '\033[0m' + f'{e}')


getDepartures()

while True:
    schedule.run_pending()
    if not schedule.get_jobs():
        conn.close()
        exit('\033[92m' + 'Time limit reached, no more requests pending' + '\033[0m')
    sleep(schedule.idle_seconds())