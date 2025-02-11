# VVOScraper

Scraping all interesting information about public transport connections/departures of one station and analysing them.

### Usage

To initialize the database, run 'initializeDatabase.py' once. Set the interval, number of departures fetched per request and end time of the schedule loop in 'scraper.py'. To analyise the fetched data, run 'analysis.py'. The charts will be saved as png in the 'Charts' folder.

### To Do's:

- [ ] Automatic analysis and visualization of the collected data
- [ ] run data analysis functions in parallel

### Ideas:

- [ ] run multiple requests in parallel with asyncio, if new features should be added (fetch data for multiple stops at once)
- [ ] add encryption for data
