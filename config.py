import os
from dotenv import load_dotenv


load_dotenv() #Load environment variables from the .env file

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #gets absolute path of the directory of the project

API_KEY = os.getenv("WEATHER_API_KEY")  #Retrieve the OpenWeather API key from environment variables
DEFAULT_CITY = os.getenv("WEATHER_CITY", "Holzminden") #Set default city (fallback to "Holzminden" if not specified in .env)
DB_NAME = os.getenv("WEATHER_DB_NAME", "weather.db") #Set database file name
DB_PATH = os.path.join(BASE_DIR, DB_NAME) #Construct the full absolute path to the SQLite database file