import datetime
import os
from typing import NamedTuple

import matplotlib.pyplot as pyplot

import main as pw
import settings
import utils


DATES = '2018-01-01..2018-12-31'
MIN_DATE, MAX_DATE = map(
    lambda d: datetime.datetime.strptime(d.strip(), '%Y-%m-%d').date(),
    DATES.split('..', 1),
)


class FakeArgs(NamedTuple):
    config = None
    dates = DATES


def main():
    config = settings.Config()
    pw.Application(FakeArgs()).run()
    predictions = utils.load_predictions(
        os.path.abspath(config.predictions_path),
    )
    weather_data = utils.load_weather_data(os.path.abspath(config.data_path))
    _draw_plot(predictions, weather_data)


def _draw_plot(predictions, weather_data):
    x = list(predictions.keys())
    y1 = list(predictions.values())
    y2 = [
        data.avg_temp
        for data in reversed(weather_data)
        if MIN_DATE <= data.date < MAX_DATE
    ]
    diffs = [
        abs(_y1 - _y2) for _y1, _y2 in zip(y1, y2)
    ]
    diffs.sort()
    mean_diff = sum(diffs) / len(diffs)
    med_diff = diffs[len(diffs) // 2]
    pyplot.title('Mean error = %.1f     Median error = %.1f' % (
        mean_diff, med_diff,
    ))
    pyplot.plot(x, y1, label='Predicted temperature')
    pyplot.plot(x, y2, label='Real temperature')
    _ = pyplot.legend()
    pyplot.xlabel('2018 year')
    pyplot.ylabel('Degrees of Celsius')
    pyplot.show()


if __name__ == '__main__':
    main()
