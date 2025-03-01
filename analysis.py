import os

import sqlite3 as sql
import matplotlib.pyplot as plt
import seaborn as sns
import pandas


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
    departures_per_line()
    #departures_per_platform()
    #departures_per_network()
    #departures_per_type()
    #departures_per_status()
    #average_delay_per_line()
    #average_delay_per_platform()
    #status_heatmap()
    #delay_heatmap()

    conn.close()


def handle_plot_files(name):
    plt.tight_layout()
    filePath.rstrip('/')
    if savePlots: 
        plt.savefig(f'{filePath}/{name}.{fileType}', bbox_inches='tight')
    if showPlots: 
        plt.show()
    plt.close()


def departures_per_line():
    try:
        query = "SELECT LineId, COUNT(*) AS departures FROM main_table GROUP BY LineId ORDER BY departures DESC"
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='LineId', y='departures', order=df['LineId'])
        plt.xticks(rotation=-90)
        handle_plot_files('departures_per_line')
    except Exception as e:
        print(f'an exception occured while analysing departures per line: {e}')


def departures_per_platform():
    try:
        query = "SELECT Platform, COUNT(*) AS departures FROM main_table GROUP BY Platform ORDER BY departures DESC"
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='Platform', y='departures', order=df['Platform'])
        handle_plot_files('departures_per_platform')
    except Exception as e:
        print(f'an exception occured while analysing departures per platform: {e}')


def departures_per_network():
    try:
        query = "SELECT Network, COUNT(*) AS departures FROM main_table GROUP BY Network ORDER BY departures DESC"
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='Network', y='departures', order=df['Network'])
        handle_plot_files('departures_per_network')
    except Exception as e:
        print(f'an exception occured while analyzing departures per Network: {e}')
        

def departures_per_type():
    try:
        query = "SELECT TransportationType as type, COUNT(*) as departures FROM main_table GROUP BY type ORDER BY departures"
        df = pandas.read_sql_query(query, conn)
        sns.barplot(df, x='type', y='departures', order=df['type'])
        handle_plot_files('departures_per_type')
    except Exception as e:
        print(f'an exception occured while analysing departures per transportation type: {e}')


def departures_per_status():
    try:
        query = "SELECT Status, COUNT(*) as departures FROM main_table GROUP BY Status"
        df = pandas.read_sql_query(query, conn)
        colorMap = {'Delayed' : 'red', 'InTime' : 'green', 'Unknown' : 'grey'}
        sns.barplot(df, x='Status', y='departures', hue='Status', palette=colorMap)
        handle_plot_files('departures_per_status')
    except Exception as e:
        print(f'an exception occured while analysing departures per delay status: {e}')


def status_heatmap():
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
        handle_plot_files('status_heatmap')
    except Exception as e:
        print(f'an exception occured while analysing status over time: {e}')


def average_delay_per_line():
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
        handle_plot_files('average_delay_per_line')
    except Exception as e:
        print(f'an exception occured while analysing average delay per line: {e}')


def average_delay_per_platform():
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
        handle_plot_files('average_delay_per_platform')
    except Exception as e:
        print(f'an exception occured while analysing average delay per platform: {e}')


def delay_heatmap():
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
        handle_plot_files('delay_heatmap')
    except Exception as e:
        print(f'an exception occured while creating delay heatmap: {e}')


main()