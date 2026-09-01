import sqlite3
import json
import os
import requests
from weather_api import get_weather
import datetime as dt
import time
from database import init_db
from config import DB_PATH, DEFAULT_CITY
from database import get_connection_to_db

def migrate_from_json(json_filename, db_filename):
    """ Has been used to migrate data from JSON file to
    SQLlite DB at the start of the project and observation """
    if not os.path.exists(json_filename):  # Checks if a json.file exists in OS
        print(f"File {json_filename} does not exist")
        return

    with open(json_filename, "r", encoding="utf-8") as jf:  # Opens JSON file in "Read Mode"
        data = json.load(jf) # loads JSON array into a Python dictionary list

    conn = sqlite3.connect(db_filename) # Connects to DB
    cursor = conn.cursor()

    for entry in data:
        # Makes a tuple to correctly migrate data from JSON file to DB
        values = (
            entry.get("timestamp"),
            entry.get("city"),
            entry.get("state"),
            entry.get("temp"),
            entry.get("pressure"),
            entry.get("humidity"),
            entry.get("clouds")
        )
        # Migrates every existing in JSON record to DB (accordingly)
        cursor.execute('''  
            INSERT INTO weather (timestamp,city,state,temp,pressure,humidity,clouds)
            VALUES (?,?,?,?,?,?,?)
        ''', values)

    conn.commit() # Commits changes to DB
    conn.close()
    print(f"Migrated from {json_filename} to {db_filename} is complete. # of recordings: {len(data)}")


def show_last_records(n=5):
    conn = get_connection_to_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM weather ORDER BY id DESC LIMIT ?''', (n,))
    rows = cursor.fetchall()
    print(f"Last{n} recordings:")
    for row in rows:
        print(row)
    conn.close()




def log_weather_db(city=None):
    """ Logs current weather data from Holzminden (can be changed to any other city) into DB"""

    if city is None:
        city = DEFAULT_CITY

    timestamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        current_data = get_weather(city) # Retrieves data from API (Weather_api module) as dictionary
        if not current_data:
            print(f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No data found for {city}. Skipping.")
            return

        with sqlite3.connect(DB_PATH) as conn:     # Opens DB
            cursor = conn.cursor()               # Connects cursor to execute commands
             #  Arranges data from weather API into tuple to prepare it for recording
            weather_data = (
                timestamp,
                city,
                current_data["state"],
                current_data["temp"],
                current_data["pressure"],
                current_data["humidity"],
                current_data["clouds"]
            )

            cursor.execute('''
                INSERT INTO weather(timestamp,city,state,temp,pressure,humidity,clouds)
                VALUES (?,?,?,?,?,?,?)''', weather_data)    # Takes data from tuple and write it into DB tables accordinly


        print(f"---NEW RECORDING---\n Time: {timestamp} | City: {city} | State: {weather_data[2]} | Temp: {weather_data[3]} °C| Pressure: {weather_data[4]}hPa | Humidity: {weather_data[5]}% | Clouds: {weather_data[6]}%")
    except requests.exceptions.ConnectionError:  # Secures a script from crush while no internet connection
        print(f"[{timestamp}] Connection error. No internet access.]")
    except Exception as e:   # Secures a script from crush and logs an error to the txt file
        print(f"[{timestamp}] Unexpected error in log_weather_db: {e}. Check 'error_log.txt' for more information.")
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {e}\n")


if __name__ == "__main__":
    """ The main function of the logger """
    init_db()  # Ensures DB is ready and exists
    print("Logger has been started by user")

    while True:
        try:
            now = dt.datetime.now()
            if now.minute == 0 and now.hour % 3 == 0: # Determines an exact time to log data (every 3 hours from 00:00)
                print(f"Recordings time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                log_weather_db() # Logger is set up for a Default city, can be changed
                time.sleep(61) # Makes sure that only one recording at a time is being commited
            time.sleep(30)
        except KeyboardInterrupt: # Arrange a secure way to stop the logger
            print("Logger has been stopped by user")
            break
        except Exception as e: # Secures when unknown error accures
            print(f"Error while logging data: {e}")
            time.sleep(60)