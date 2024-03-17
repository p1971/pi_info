import sys

from dataclasses import dataclass
from datetime import datetime

from pyowm.owm import OWM
from pytz import timezone

@dataclass
class ForecastInfo:
    reftime: str
    description: str
    temperature: float
    weather_code: str

class WeatherInfo:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    # pylint: disable=too-few-public-methods
    def __init__(self,
                 location,
                 reftime,
                 description,
                 temperature,
                 max_temperature,
                 min_temperature,
                 sunrise: datetime,
                 sunset: datetime,
                 weather_code,
                 forecast: ForecastInfo):
        self.location = location
        self.reftime = reftime.astimezone(timezone("Europe/London"))
        self.description = description
        self.temperature = temperature
        self.max_temperature = max_temperature
        self.min_temperature = min_temperature
        self.sunrise = sunrise.astimezone(timezone("Europe/London"))
        self.sunset = sunset.astimezone(timezone("Europe/London"))
        self.weather_code = weather_code
        self.forecasts = forecast

class WeatherService:
    def __init__(self, api_key, city_id):
        self.api_key = api_key
        self.city_id = city_id

    def get_weather(self):
        owm = OWM(self.api_key)
        weather_mgr = owm.weather_manager()

        weather = weather_mgr.weather_at_id(self.city_id).weather

        temperature = weather.temperature('celsius')

        forecast = weather_mgr.forecast_at_id(self.city_id, '3h', 4).forecast
        forecasts = []

        for hourly_forecast in forecast:
            forecasts.append(ForecastInfo(hourly_forecast.reference_time('date'),
                hourly_forecast.detailed_status,
                round(hourly_forecast.temperature('celsius')['temp'], 1),
                hourly_forecast.weather_code))

        current_weather = WeatherInfo(
            self.city_id,
            weather.reference_time('date'),
            weather.detailed_status,
            round(temperature['temp'], 1),
            round(temperature['temp_max'], 1),
            round(temperature['temp_min'], 1),
            weather.sunrise_time('date'),
            weather.sunset_time('date'),
            weather.weather_code,
            forecasts)

        return current_weather
