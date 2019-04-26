import datetime
from typing import Any
from typing import Dict

import aiohttp

import utils
import web.clients.base as base


ZONES = {
    'moscow': 'Moscow',
}


class Client(base.Client):
    def __init__(
            self, session: aiohttp.ClientSession,
            client_config: Dict[str, Any]):
        super().__init__(session, client_config)

    async def collect_weather_of_city(
            self, city: str, date: datetime.date) -> utils.WeatherData:
        city = city.lower()
        if city not in ZONES:
            raise base.UnsupportedZone(f'Zone \'{city}\' is unsupported')
        response = await self._request(
            method='get',
            url=self.url + 'history.json',
            params={
                'key': self.token,
                'dt': date.strftime('%Y-%m-%d'),
                'q': ZONES[city],
            },
        )
        data = (await response.json())['forecast']['forecastday'][0]
        avg_pres = float(int(
            sum(hour['pressure_mb'] for hour in data['hour']) / 24,
        ))
        return utils.WeatherData(
            date=date,
            max_temp=data['day']['maxtemp_c'],
            min_temp=data['day']['mintemp_c'],
            avg_temp=data['day']['avgtemp_c'],
            avg_pres=avg_pres,
            avg_humid=data['day']['avghumidity'],
            tot_precip=data['day']['totalprecip_mm'],
            max_wind=data['day']['maxwind_kph'],
        )
