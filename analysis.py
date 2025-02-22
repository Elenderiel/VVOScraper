import sqlite3 as sql
import matplotlib.pyplot as plt
import seaborn as sns
import pandas
import os


showPlots = True
savePlots = True
fileType = 'png'                    #valid file types: png, jpg, pdf, svg, tiff
filePath = './Charts'

if not os.path.isdir(filePath):
    os.makedirs(filePath)

sns.set_theme(palette='flare')

conn = sql.connect('departureDatabase.db')
cursor = conn.cursor()


def main():
    #comment out charts that are not needed
    departuresPerLine()
    departuresPerPlatform()
    departuresPerNetwork()
    departuresPerType()
    departuresPerStatus()
    averageDelayPerLine()
    averageDelayPerPlatform()
    statusHeatmap()
    delayHeatmap()

    conn.close()


def handlePlotFiles(name):
    plt.tight_layout()
    filePath.rstrip('/')
    if savePlots: 
        plt.savefig(f'{filePath}/{name}.{fileType}', bbox_inches='tight')
    if showPlots: 
        plt.show()
    plt.close()


def departuresPerLine():
    try:
        query = "SELECT LineName, COUNT(*) AS departures FROM main_table GROUP BY LineName ORDER BY departures DESC"
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='LineName', y='departures', order=df['LineName'])
        handlePlotFiles('departuresPerLine')
    except Exception as e:
        print(f'an exception occured while analysing departures per line: {e}')


def departuresPerPlatform():
    try:
        query = "SELECT Platform, COUNT(*) AS departures FROM main_table GROUP BY Platform ORDER BY departures DESC"
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='Platform', y='departures', order=df['Platform'])
        handlePlotFiles('departuresPerPlatform')
    except Exception as e:
        print(f'an exception occured while analysing departures per platform: {e}')


def departuresPerNetwork():
    try:
        query = "SELECT Network, COUNT(*) AS departures FROM main_table GROUP BY Network ORDER BY departures DESC"
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='Network', y='departures', order=df['Network'])
        handlePlotFiles('departuresPerNetwork')
    except Exception as e:
        print(f'an exception occured while analyzing departures per Network: {e}')
        

def departuresPerType():
    try:
        query = "SELECT TransportationType as type, COUNT(*) as departures FROM main_table GROUP BY type ORDER BY departures"
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='type', y='departures', order=df['type'])
        handlePlotFiles('departuresPerType')
    except Exception as e:
        print(f'an exception occured while analysing departures per transportation type: {e}')


def departuresPerStatus():
    try:
        query = "SELECT Status, COUNT(*) as departures FROM main_table GROUP BY Status"
        df = pandas.read_sql_query(query, conn)
        colorMap = {'Delayed' : 'red', 'InTime' : 'green', 'Unknown' : 'grey'}
        sns.barplot(df, x='Status', y='departures', hue='Status', palette=colorMap)
        handlePlotFiles('departuresPerStatus')
    except Exception as e:
        print(f'an exception occured while analysing departures per delay status: {e}')


def statusHeatmap():
    try:
        query = "SELECT LineId, ScheduledTime, Status from main_table ORDER BY ScheduledTime"
        df = pandas.read_sql_query(query, conn)
        valueMap = {'Delayed' : 2, 'Unknown' : 1, 'InTime' : 0}
        df['Status'] = df['Status'].map(valueMap)
        df['ScheduledTime'] = pandas.to_datetime(df['ScheduledTime'], unit='s').dt.strftime('%H:%M')
        heatMap = df.pivot(index='LineId', columns='ScheduledTime', values='Status')

        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        ax.grid(False)
        sns.heatmap(heatMap, cmap='vlag', linewidths=0.05, linecolor='#333', cbar=False, ax=ax)
        handlePlotFiles('statusHeatmap')
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
        handlePlotFiles('averageDelayPerLine')
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
        handlePlotFiles('averageDelayPerPlatform')
    except Exception as e:
        print(f'an exception occured while analysing average delay per platform: {e}')


def delayHeatmap():
    try:
        query = """
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
                """
        df = pandas.read_sql_query(query, conn)
        df['ScheduledTime'] = pandas.to_datetime(df['ScheduledTime'], unit='s').dt.strftime('%H:%M')
        heatMap = df.pivot(index='LineId', columns='ScheduledTime', values='DelayTime')

        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        ax.grid(False)
        vmax = max(abs(df['DelayTime'].min()), abs(df['DelayTime'].max()))
        sns.heatmap(heatMap, linecolor='#333', linewidths=0.1, cmap='coolwarm', ax=ax, vmax=vmax, vmin=-vmax)
        handlePlotFiles('delayHeatmap')
    except Exception as e:
        print(f'an exception occured while creating delay heatmap: {e}')


main()