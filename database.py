import mysql.connector as mysql
import sqlalchemy
from config import Config

config = Config()


class Database:
    def __init__(self):
        self.host = config.config.get('mysql', 'host')
        self.user = config.config.get('mysql', 'user')
        self.password = config.config.get('mysql', 'password')
        if not config.config.get('mysql', 'db_name'):
            self.check_db_exists(db_name='daily_us_weather_data')

    def check_db_exists(self, db_name):
        print('Checking for existing database')
        conn = mysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
        )
        db_cursor = conn.cursor()
        db_cursor.execute("SHOW DATABASES")
        databases = db_cursor.fetchall()
        if db_name not in databases:
            db_cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
            config.config.set('mysql', 'db_name', 'daily_us_weather_data')
            config.save_config()
        conn.close()

    # # Load Data
    def load_data(self, df):
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://{}:{}@{}/{}'.format(
            self.user, self.password, self.host, config.config.get('mysql', 'db_name')))
        db = mysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=config.config.get('mysql', 'db_name')
        )
        cursor = db.cursor()

        create_state_weather_table_query = """
            CREATE TABLE IF NOT EXISTS daily_state_weather_data(
                id INT(50) AUTO_INCREMENT PRIMARY KEY,
                Date DATE,
                State VARCHAR(200),
                Timezone VARCHAR(200),
                Conditions VARCHAR(200),
                Min_Temp FLOAT(20),
                Max_Temp FLOAT(20)
            )
            """

        cursor.execute(create_state_weather_table_query)
        print("Opened database successfully")

        df.to_sql(name="daily_state_weather_data", con=engine, index=False, if_exists='append')
        db.commit()
        print("Data was written to database")

        print("Cleaning out entries older than 7 days")
        delete_old_entries_query = """
            DELETE FROM daily_state_weather_data WHERE Date < (NOW() - INTERVAL 8 DAY)
            """
        cursor.execute(delete_old_entries_query)
        db.commit()

        db.close()
        print("Closed database successfully")
