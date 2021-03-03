import pandas as pd
import requests
import json
import datetime
import mysql.connector as mysql
from getpass import getpass
import sqlalchemy
import configparser


def check_db_exists(db_name):
    # Enter your MySQL credentials
    conn = mysql.connect(
        host="localhost",
        user=input("Enter username: "),
        password=getpass("Enter password: "),
    )
    db_cursor = conn.cursor()
    db_cursor.execute("SHOW DATABASES")
    databases = db_cursor.fetchall()
    if db_name not in databases:
        db_cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(db_name))


# Configuration Init
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config.get('api', 'key')
if not api_key:
    api_key = input("Enter OpenWeather API Key: ")
    config.set('api', 'key', api_key)

user = config.get('mysql', 'user')
if not user:
    user = input('Enter database username: ')
    config.set('mysql', 'user', user)

password = config.get('mysql', 'password')
if not password:
    password = input('Enter database password: ')
    config.set('mysql', 'password', password)

# Load US States
state_data = pd.read_csv('US_States.csv')

# Get previous day and convert to UNIX Utc timestamp for historical API call
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
timestamp = datetime.datetime.timestamp(yesterday)

# Extract Data
weather_list = []
# Get weather values for all states
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

weather_json = json.dumps(weather_list)

# Transform Data
print('Normalizing JSON data from API')

df = pd.json_normalize(json.loads(weather_json), ['Data', 'hourly', 'weather'],
                       meta=['State', ['Data', 'timezone'], ['Data', 'hourly', 'temp']]).rename(
    columns={'Data.timezone': 'Timezone', 'main': 'Conditions', 'Data.hourly.temp': 'Temp'}).drop(
    ['id', 'description', 'icon'], axis=1)

flat_df = df.groupby(['State', 'Timezone']).agg({'Temp': [min, max], 'Conditions': [max]}).reset_index()
flat_df['Date'] = yesterday.strftime('%a %b %d %Y')
flat_df.columns = ['State', 'Timezone', 'Min_Temp', 'Max_Temp', 'Conditions', 'Date']

# # Load Data
engine = sqlalchemy.create_engine('mysql+mysqlconnector://{}:{}@localhost/daily_us_weather_data'.format(user, password))
db = mysql.connect(
    host="localhost",
    user=user,
    password=password,
    database=config.get('mysql', 'db_table_name')
)
cursor = db.cursor()

create_state_weather_table_query = """
    CREATE TABLE IF NOT EXISTS daily_state_weather_data(
        id INT(50) AUTO_INCREMENT PRIMARY KEY,
        Date VARCHAR(200),
        State VARCHAR(200),
        Timezone VARCHAR(200),
        Conditions VARCHAR(200),
        Min_Temp FLOAT(20),
        Max_Temp FLOAT(20)
    )
    """

cursor.execute(create_state_weather_table_query)
print("Opened database successfully")

flat_df.to_sql(name="daily_state_weather_data", con=engine, index=False, if_exists='append')
print("Data was written to database")

db.close()
print("Closed database successfully")

# Save Configuration File
with open('config.ini', 'w') as config_file:
    config.write(config_file)
