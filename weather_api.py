from enum import Enum
import requests
from config import API_KEY, DEFAULT_CITY

class WeatherState(Enum):
    """
    Enum representing standardized weather states.
    Maps fine-grained API codes into broader categories for Markov chain analysis.
        """
    CLEAR = 1
    FEW_CLOUDS = 2
    PARTLY_CLOUDY = 3
    BROKEN_CLOUDS = 4
    CLOUDY = 5
    RAINY = 6
    SNOWY = 7
    STORM = 8
    FOGGY = 9


def get_weather(city=None):
    """Fetches current weather data for a given city from OpenWeatherMap API
    and maps the condition to a standardized WeatherState. """

    if city is None:
        city = DEFAULT_CITY

    if not API_KEY:
        raise ValueError("API Key is missing. Please set WEATHER_API_KEY in .env file")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    request = requests.get(url)
    data = request.json()
    if data["cod"] == 200:
        weather = data['weather'][0]['id']
        if weather == 800:
            state = WeatherState.CLEAR
        elif weather == 801:
            state = WeatherState.FEW_CLOUDS
        elif weather == 802:
            state = WeatherState.PARTLY_CLOUDY
        elif weather == 803:
            state = WeatherState.BROKEN_CLOUDS
        elif weather == 804:
            state = WeatherState.CLOUDY
        elif 300 <= weather <= 321 or weather >= 500 and weather <= 531:
            state = WeatherState.RAINY
        elif weather >= 600 and weather <= 622:
            state = WeatherState.SNOWY
        elif weather >= 200 and weather <= 232:
            state = WeatherState.STORM
        elif weather == 741:
            state = WeatherState.FOGGY
        else:
            state = WeatherState.CLOUDY
        return {
            "state": state.name,
            "temp": data["main"]["temp"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "clouds": data["clouds"]["all"],
        }
    else:
        return None