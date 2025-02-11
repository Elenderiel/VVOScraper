import sqlite3 as sql
import matplotlib.pyplot as plt
import seaborn as sns
import pandas

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

def statusHeatmap():
    try:
        cursor.execute("SELECT LineId, ScheduledTime, Status from main_table ORDER BY ScheduledTime")
        data = cursor.fetchall()
        df = pandas.DataFrame(data, columns=['LineId', 'scheduledTime', 'status'])
        valueMap = {'Delayed' : 2, 'Unknown' : 1, 'InTime' : 0}
        df['status'] = df['status'].map(valueMap)
        df['scheduledTime'] = pandas.to_datetime(df['scheduledTime'], unit='s').dt.strftime('%H:%M')
        heatMap = df.pivot(index='LineId', columns='scheduledTime', values='status')
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        ax.grid(False)
        sns.heatmap(heatMap, cmap='vlag', linewidths=0.05, linecolor='#333', cbar=False, ax=ax)
        plt.show()
    except Exception as e:
        print(f'an exception occured while analysing status over time: {e}')

def averageDelayPerLine():
    try:
        query = """
                WITH latest_delays AS (
                    SELECT MainId, DelayTime
                    FROM delay_table d1
                    WHERE TimeStamp = (
                        SELECT MAX(d2.TimeStamp) FROM delay_table d2 WHERE d1.MainId = d2.MainId
                    )
                )
                SELECT m.LineId, AVG(ld.DelayTime) AS avgDelay
                FROM main_table m
                JOIN latest_delays ld ON m.Id = ld.MainId
                GROUP BY m.LineId
                ORDER BY avgDelay DESC;
                """
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='LineId', y='avgDelay', order=df['LineId'])
        plt.xticks(rotation=-90)
        plt.show()
    except Exception as e:
        print(f'an exception occured while analysing average delay per line: {e}')

def averageDelayPerPlatform():
    try:
        query = """
                WITH latest_delays AS (
                    SELECT MainId, DelayTime
                    FROM delay_table d1
                    WHERE TimeStamp = (
                        SELECT MAX(d2.TimeStamp) FROM delay_table d2 WHERE d1.MainId = d2.MainId
                    )
                )
                SELECT m.Platform, AVG(ld.DelayTime) AS avgDelay
                FROM main_table m
                JOIN latest_delays ld ON m.Id = ld.MainId
                GROUP BY m.Platform
                ORDER BY avgDelay DESC;
                """
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='Platform', y='avgDelay', order=df['Platform'])
        plt.show()
    except Exception as e:
        print(f'an exception occured while analysing average delay per platform: {e}')

def delayHeatmap():
    try:
        cursor.execute("""
                        WITH latestDelays AS (
                            SELECT MainId, DelayTime
                            FROM delay_table d1
                            WHERE TimeStamp = (
                                    SELECT MAX(d2.TimeStamp) FROM delay_table d2 WHERE d1.MainId = d2.MainId
                            )
                        )
                        SELECT m.LineId, m.ScheduledTime, ld.DelayTime
                        FROM main_table m
                        JOIN latestDelays ld ON ld.MainId = m.Id
                        ORDER BY ld.DelayTime
                        """)
        data = cursor.fetchall()
        df = pandas.DataFrame(data, columns=['LineId', 'ScheduledTime', 'DelayTime'])
        df['ScheduledTime'] = pandas.to_datetime(df['ScheduledTime'], unit='s').dt.strftime('%H:%M')
        heatMap = df.pivot(index='LineId', columns='ScheduledTime', values='DelayTime')
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        ax.grid(False)
        vmax = max(abs(df['DelayTime'].min()), abs(df['DelayTime'].max()))
        sns.heatmap(heatMap, linecolor='#333', linewidths=0.1, cmap='coolwarm', ax=ax, vmax=vmax, vmin=-vmax)
        plt.show()
    except Exception as e:
        print(f'an exception occured while creating delay heatmap: {e}')

delayHeatmap()
conn.close()