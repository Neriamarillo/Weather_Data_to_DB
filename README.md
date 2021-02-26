# ETL Process for weather data of all 50 US States.

# Scraping
Scraped the [LatLong](https://www.latlong.net/category/states-236-14.html) website to obtain all the US States 
latitude and longitude values and save them to a .csv file.

## Extraction
Extract weather data from OpenWeather API. Historical hourly data from each US state recorded in the 
previous day is used.

## Transform
Transformed JSON API Response to a Pandas DataFrame to show:
- State Name
- Timezone
- Weather Conditions for the min and max temperatures for the day
- Minimum Temperature of day
- Maximum Temperature of day

## Load
Load the dataframe to a MySQL database hosted locally.