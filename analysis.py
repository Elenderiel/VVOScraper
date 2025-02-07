import sqlite3 as sql
import pandas
import matplotlib.pyplot as plt
import seaborn as sns

conn = sql.connect('departureDatabase.db')
cursor = conn.cursor()
sns.set_theme(palette='flare')

def departuresPerLine():
    try:
        cursor.execute("SELECT lineName, COUNT(*) AS departures FROM main_table GROUP BY lineName ORDER BY departures DESC")
        departures = cursor.fetchall()
        df = pandas.DataFrame(departures, columns=['line', 'departures'])
        sns.barplot(df, x='line', y='departures', order=df['line'])
        plt.show()
    except Exception as e:
        print(f'an exception occured while analysing departures per line: {e}')

def departuresPerPlatform():
    try:
        cursor.execute("SELECT Platform, COUNT(*) AS departures FROM main_table GROUP BY Platform ORDER BY departures DESC")
        data = cursor.fetchall()
        df = pandas.DataFrame(data, columns=['platform', 'departures'])
        sns.barplot(df, x='platform', y='departures', order=df['platform'])
        plt.show()
    except Exception as e:
        print(f'an exception occured while analysing departures per platform: {e}')

def departuresPerNetwork():
    try:
        cursor.execute("SELECT Network, COUNT(*) AS departures FROM main_table GROUP BY Network ORDER BY departures DESC")
        data = cursor.fetchall()
        df = pandas.DataFrame(data, columns=['network', 'departures'])
        sns.barplot(df, x='network', y='departures', order=df['network'])
        plt.show()
    except Exception as e:
        print(f'an exception occured while analyzing departures per Network: {e}')

def departuresPerType():
    try:
        cursor.execute("SELECT TransportationType, COUNT(*) as departures FROM main_table GROUP BY TransportationType ORDER BY departures")
        data = cursor.fetchall()
        df = pandas.DataFrame(data, columns=['type', 'departures'])
        sns.barplot(df, x='type', y='departures', order=df['type'])
        plt.show()
    except Exception as e:
        print(f'an exception occured while analysing departures per transportation type: {e}')

def departuresPerStatus():
    try:
        cursor.execute("SELECT Status, COUNT(*) as departures FROM main_table GROUP BY Status")
        data = cursor.fetchall()
        df = pandas.DataFrame(data, columns=['status', 'departures'])
        colorMap = {'Delayed' : 'red', 'InTime' : 'green', 'Unknown' : 'grey'}
        sns.barplot(df, x='status', y='departures', hue='status', palette=colorMap)
        plt.show()
    except Exception as e:
        print(f'an exception occured while analysing departures per delay status: {e}')

departuresPerStatus()
conn.close()