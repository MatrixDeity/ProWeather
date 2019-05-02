import datetime
import os

import aiohttp
import asyncio_pool

import settings
import utils
import web.clients.apixu as apixu
import web.clients.base as base
import web.clients.wunderground as wunderground


class Collector:
    def __init__(self, config: settings.Config):
        self.session = aiohttp.ClientSession()
        self.clients = (
            apixu.Client(self.session, config.apixu),
            wunderground.Client(self.session, config.wunderground),
        )
        self.zone = config.zone
        self.data_path = os.path.abspath(config.data_path)
        self.start_date = config.start_date
        self.async_number = config.async_number
        self.weathers_by_dates = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close_session()

    async def collect_weather(self):
        async def task(client: base.Client, date: datetime.date):
            weather = await client.collect_weather_of_city(self.zone, date)
            self._aggregate_weathers(date, weather)

        async with asyncio_pool.AioPool(size=self.async_number) as pool:
            for client in self.clients:
                if client.disabled:
                    continue
                for date in utils.dates_between(self.start_date):
                    await pool.spawn(task(client, date))

    async def close_session(self):
        await self.session.close()

    def _aggregate_weathers(
            self, date: datetime.date, weather: utils.WeatherData):
        if date in self.weathers_by_dates:
            old_weather = self.weathers_by_dates[date]
            self.weathers_by_dates[date] = old_weather.aggregate(weather)
        else:
            self.weathers_by_dates[date] = weather

    def save_weather_data(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        utils.dump_weather_data(
            self.weathers_by_dates.values(), self.data_path,
        )


async def grab_weather_once(config: settings.Config):
    async with Collector(config) as collector:
        await collector.collect_weather()
        collector.save_weather_data()
