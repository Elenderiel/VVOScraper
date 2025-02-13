# VVOScraper

Scraping all interesting information about public transport connections/departures of one station and analysing them.

### Usage

To initialize the database, run 'initializeDatabase.py'. Set the interval, number of departures fetched per request and end time of the schedule loop in 'scraper.py'. To analyse the fetched data, run 'analysis.py'. The charts will be saved in the 'Charts' folder. Set the file type and the needed charts in the script

### To Do's:

- [ ] analyse delay development over time
- [ ] dynamic spacing of plots

### Ideas:

- [ ] run multiple requests in parallel (fetch data for multiple stops at once)
- [ ] add encryption for data
