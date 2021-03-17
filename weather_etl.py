import pandas as pd
import requests
import json
import datetime

from config import Config
from database import Database

config = Config()
db = Database()
weather_list = []


def extract_data():
    # Extract Data
    # Get weather values for all states
    api_key = config.config.get('api', 'key')
    print('Getting data from API')
    for state in state_data.State:
        selected_state = state_data.loc[state_data.State == '{}'.format(state)]
        lat = selected_state.Lat.to_string(index=False)
        lon = selected_state.Lon.to_string(index=False)
        weather_dict = {
            'State': [],
            'Data': []
        }
        # Historic Weather Data URL
        weather_api_url = "https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={}&lon={}&dt={}&units=imperial&appid={}".format(
            lat, lon, int(timestamp), api_key)

        response = requests.get(weather_api_url)
        response.raise_for_status()
        payload_data = response.json()
        weather_dict['State'] = state
        weather_dict['Data'] = payload_data
        weather_list.append(weather_dict)


# Transform Data
def transform_data():
    print('Normalizing JSON data from API')
    weather_json = json.dumps(weather_list)

    df = pd.json_normalize(json.loads(weather_json), ['Data', 'hourly', 'weather'],
                           meta=['State', ['Data', 'timezone'], ['Data', 'hourly', 'temp']]).rename(
        columns={'Data.timezone': 'Timezone', 'main': 'Conditions', 'Data.hourly.temp': 'Temp'}).drop(
        ['id', 'description', 'icon'], axis=1)

    flat_df = df.groupby(['State', 'Timezone']).agg({'Temp': [min, max], 'Conditions': [max]}).reset_index()
    flat_df['Date'] = yesterday.date()
    flat_df.columns = ['State', 'Timezone', 'Min_Temp', 'Max_Temp', 'Conditions', 'Date']
    return flat_df


# Load US States
state_data = pd.read_csv('US_States.csv')

# Get previous day and convert to UNIX Utc timestamp for historical API call
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
timestamp = datetime.datetime.timestamp(yesterday)

extract_data()
weather_df = transform_data()
db.load_data(weather_df)
