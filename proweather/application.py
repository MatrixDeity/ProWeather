import asyncio
import os

import settings
import utils
import web.collector as collector


class Application:
    def __init__(self):
        self.config = settings.Config()

    def run(self):
        self._collect_weather_data()
        print(utils.load_weather_data(self.config.data_path))

    def _collect_weather_data(self):
        data_path = os.path.abspath(self.config.data_path)
        if not os.path.exists(data_path):
            asyncio.run(collector.grab_weather_once(self.config))
