import datetime
from typing import Any
from typing import Dict

import aiohttp

import utils
import web.clients.base as base


ZONES = {
    'moscow': 'RU/Moscow',
}


# TODO: support Weather Underground later
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
        url = '{base_url}/{token}/history_{date}/q/{zone}.json'.format(
            base_url=self.url,
            token=self.token,
            date=date.strftime('%Y%m%d'),
            zone=ZONES[city],
        )
        response = await self._request(
            method='get',
            url=url,
        )
        data = (await response.json())['history']['dailysummary'][0]
        return utils.WeatherData(
            date=date,
            max_temp=data['maxtempm'],
            min_temp=data['mintempm'],
            avg_temp=data['meantempm'],
            avg_pres=data['meanpressurem'],
            avg_humid=data['meanhumidity'],
            tot_precip=data['precipm'],
            max_wind=data['maxwindm'],
        )
