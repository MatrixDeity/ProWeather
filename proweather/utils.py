import datetime
import pickle
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Tuple


class WeatherData(NamedTuple):
    date: datetime.date
    max_temp: float
    min_temp: float
    avg_temp: float
    avg_pres: float
    avg_humid: float
    tot_precip: float
    max_wind: float

    @staticmethod
    def get_fields() -> Tuple[str]:
        return tuple(WeatherData._fields)

    def aggregate(self, other: 'WeatherData') -> 'WeatherData':
        return WeatherData(
            date=self.date,
            max_temp=(self.max_temp + other.max_temp) / 2,
            min_temp=(self.min_temp + other.min_temp) / 2,
            avg_temp=(self.avg_temp + other.avg_temp) / 2,
            avg_pres=(self.avg_pres + other.avg_pres) / 2,
            avg_humid=(self.avg_humid + other.avg_humid) / 2,
            tot_precip=(self.tot_precip + other.tot_precip) / 2,
            max_wind=(self.max_wind + other.max_wind) / 2,
        )


def dump_weather_data(weather_data: Iterable[WeatherData], target: str):
    weather_data = list(weather_data)
    with open(target, 'wb') as file:
        pickle.dump(weather_data, file)


def load_weather_data(target: str) -> List[WeatherData]:
    with open(target, 'rb') as file:
        weather_data = pickle.load(file)
    return weather_data
