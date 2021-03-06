# ETL Process for weather data of all 50 US States.

# Scraping
Scraped the [LatLong](https://www.latlong.net/category/states-236-14.html) website using Selenium to obtain all the US States 
latitude and longitude values and save them to a .csv file.

## Extraction
Extract weather data from OpenWeather API. Historical hourly data from each US state recorded in the 
previous day is used.

## Transform
Transformed JSON API Response to a Pandas DataFrame to show:
- Date of collection
- State Name
- Timezone
- Weather Conditions for the min and max temperatures for the day
- Minimum Temperature of day
- Maximum Temperature of day

## Load
Load the dataframe to a MySQL database hosted locally using the mysql.connector.

## Visualization
Using Metabase as a visualization tool, we can show the US map to view the average minimun and maximum temperatures for all 50 states. 

<img width="1437" alt="image" src="https://user-images.githubusercontent.com/6305190/110218789-35988100-7e81-11eb-856e-60db0a0a5f83.png">
