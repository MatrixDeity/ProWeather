import argparse
import asyncio
import datetime
import os
import sys

import ml.supervisor as supervisor
import settings
import utils
import web.collector as collector


class BadPythonVersion(EnvironmentError):
    pass


class Application:
    def __init__(self, args):
        self.config = settings.Config(args.config)
        if '..' in args.dates:
            date_begin, date_end = map(
                lambda d: datetime.datetime.strptime(
                    d.strip(), '%Y-%m-%d',
                ).date(),
                args.dates.split('..', 1),
            )
            self.prediction_dates = list(
                utils.dates_between(date_begin, date_end),
            )
        else:
            self.prediction_dates = [
                datetime.datetime.strptime(args.dates.strip(), '%Y-%m-%d'),
            ]

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
        supervisor.predict_weather_once(self.config, self.prediction_dates)


def main():
    if sys.version_info < (3, 7):
        raise BadPythonVersion('ProWeather requires Python 3.7+')

    args = _parse_args()
    Application(args).run()


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', type=str, help='Path to config file',
    )
    parser.add_argument(
        'dates', type=str, help='Interval of dates to weather predict',
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
