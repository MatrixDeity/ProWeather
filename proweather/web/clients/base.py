import abc
import datetime
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp

import utils


class UnsupportedZone(Exception):
    pass


class Client:
    def __init__(
            self, session: aiohttp.ClientSession,
            client_config: Dict[str, Any]):
        self.session = session
        self.url = client_config['url']
        self.token = client_config['token']
        self.disabled = client_config.get('disabled', False)

    @abc.abstractmethod
    async def collect_weather_of_city(
            self, city: str, date: datetime.date) -> utils.WeatherData:
        """Override me"""

    async def _request(
            self,
            method: str,
            url: str,
            json: Optional[dict] = None,
            headers: Optional[dict] = None,
            params: Optional[dict] = None,
            **kwargs) -> aiohttp.ClientResponse:
        response = await self.session.request(
            method=method,
            url=url,
            json=json,
            headers=headers,
            params=params,
            **kwargs,
        )
        response.raise_for_status()

        return response
