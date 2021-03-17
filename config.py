import configparser
from scraper import fetch_states
import os


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.run_config()

    def is_first_run(self):
        if self.config.getboolean('init_run', 'is_first_run'):
            self.config.set('init_run', 'is_first_run', "False")
        if not os.path.exists('US_States.csv') or os.stat('US_States.csv').st_size == 0:
            fetch_states()

    def run_config(self):
        self.is_first_run()
        api_key = self.config.get('api', 'key')
        if not api_key:
            api_key = input("Enter OpenWeather API Key: ")
            self.config.set('api', 'key', api_key)

        host = self.config.get('mysql', 'host')
        if not host:
            host = input('Enter Hostname: ')
            self.config.set('mysql', 'host', host)

        user = self.config.get('mysql', 'user')
        if not user:
            user = input('Enter database username: ')
            self.config.set('mysql', 'user', user)

        password = self.config.get('mysql', 'password')
        if not password:
            password = input('Enter database password: ')
            self.config.set('mysql', 'password', password)
        self.save_config()

    # Save Configuration File
    def save_config(self):
        with open('config.ini', 'w') as config_file:
            self.config.write(config_file)
