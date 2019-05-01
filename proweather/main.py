import asyncio
import os
import sys

import ml.supervisor as supervisor
import settings
import web.collector as collector


class BadPythonVersion(EnvironmentError):
    pass


class Application:
    def __init__(self):
        self.config = settings.Config()

    def run(self):
        self._collect_weather_data()
        self._train_model()
        self._predict_weather()

    def _collect_weather_data(self):
        data_path = os.path.abspath(self.config.data_path)
        if not os.path.exists(data_path):
            asyncio.run(collector.grab_weather_once(self.config))

    def _train_model(self):
        model_path = os.path.abspath(self.config.model_path)
        if not os.path.exists(model_path):
            supervisor.train_model_once(self.config)

    def _predict_weather(self):
        supervisor.predict_weather_once(self.config)


def main():
    if sys.version_info < (3, 7):
        raise BadPythonVersion('ProWeather requires Python 3.7+')

    Application().run()


if __name__ == '__main__':
    main()
