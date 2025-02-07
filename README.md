# VVOScraper

Scraping all interesting information about public transport connections/departures of one station and analysing them.

### Usage

To initialize the database, run 'initializeDatabase.py' once. Set the interval, number of departures fetched per request and end time of the schedule loop in 'scraper.py'

### To Do's:

- [ ] Automatic analysis and visualization of the collected data
- [ ] run data analysis functions in parallel

### Ideas:

- [ ] run multiple requests in parallel with asyncio, if new features should be added
- [ ] add encryption for data
