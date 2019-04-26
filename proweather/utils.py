import dataclasses
import datetime
import pickle
from typing import Iterable
from typing import List


@dataclasses.dataclass
class WeatherData:
    date: datetime.date
    max_temp: float
    min_temp: float
    avg_temp: float
    avg_pres: float
    avg_humid: float
    tot_precip: float
    max_wind: float

    def aggregate(self, other: 'WeatherData'):
        self.max_temp = (self.max_temp + other.max_temp) / 2
        self.min_temp = (self.min_temp + other.min_temp) / 2
        self.avg_temp = (self.avg_temp + other.avg_temp) / 2
        self.tot_precip = (self.tot_precip + other.tot_precip) / 2
        self.max_wind = (self.max_wind + other.max_wind) / 2


def dump_weather_data(weather_data: Iterable[WeatherData], target: str):
    weather_data = list(weather_data)
    with open(target, 'wb') as file:
        pickle.dump(weather_data, file)


def load_weather_data(target: str) -> List[WeatherData]:
    with open(target, 'rb') as file:
        weather_data = pickle.load(file)
    return weather_data
