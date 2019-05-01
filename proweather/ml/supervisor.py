import datetime
import os
from typing import Optional
from typing import Tuple

import pandas
import tensorflow

import settings
import utils


class Supervisor:
    def __init__(self, config: settings.Config):
        self.data_path = os.path.abspath(config.data_path)
        self.weather_frame = pandas.DataFrame()
        self.features = []
        self.max_nth_year = config.max_nth_year
        self.start_date = config.start_date
        self.years_insurance = config.years_insurance
        self.model_path = os.path.abspath(config.model_path)
        self.hidden_units = config.hidden_units
        self.index = 'date'
        self.train_iterations = config.train_iterations
        self.train_steps = config.train_steps
        self.prediction_date = config.prediction_date

    def train(self):
        self._read_weather_data()
        train_frame = self._make_train_frame()
        x, y = self._split_frame(train_frame, 'avg_temp')
        self._fit_model(x, y)

    def predict(self):
        self._read_weather_data()
        prediction_frame = self._make_prediction_frame()
        x, _ = self._split_frame(prediction_frame)
        prediction = self._predict_one_day(x)
        print(
            'Weather for %s: %.0fC.' % (
                self.prediction_date.strftime('%d.%m.%Y'), prediction[0],
            ),
        )

    def _read_weather_data(self):
        weather_data = utils.load_weather_data(self.data_path)
        columns = utils.WeatherData.get_fields()
        self.weather_frame = pandas.DataFrame(
            data=weather_data,
            columns=columns,
        ).set_index(self.index)
        self.features = [
            feature for feature in columns if feature != self.index
        ]

    def _prepare_data_frame(self, frame: pandas.DataFrame) -> pandas.DataFrame:
        for feature in self.features:
            for n in range(1, self.max_nth_year + 1):
                frame = self._derive_nth_year_feature(frame, feature, n)
        frame = frame.apply(pandas.to_numeric, errors='coerce')
        return frame.dropna().reset_index().drop(self.index, axis=1)

    def _fit_model(self, x: pandas.DataFrame, y: pandas.Series):
        feature_cols = [
            tensorflow.feature_column.numeric_column(col) for col in x.columns
        ]
        regressor = tensorflow.estimator.DNNRegressor(
            feature_columns=feature_cols,
            hidden_units=self.hidden_units,
            model_dir=self.model_path,
        )
        message = 'INFO:tensorflow:Training progress: %.0f%%'
        for iteration in range(self.train_iterations):
            print(message % (iteration / self.train_iterations * 100))
            regressor.train(
                input_fn=_wx_input_fn(x, y),
                steps=self.train_steps,
            )

    def _predict_one_day(self, x: pandas.DataFrame) -> Tuple[float]:
        feature_cols = [
            tensorflow.feature_column.numeric_column(col) for col in x.columns
        ]
        regressor = tensorflow.estimator.DNNRegressor(
            feature_columns=feature_cols,
            hidden_units=self.hidden_units,
            model_dir=self.model_path,
        )
        prediction = regressor.predict(
            input_fn=_wx_input_fn(x, None, 1, False),
        )
        return tuple(next(prediction)['predictions'])

    def _derive_nth_year_feature(
            self, frame: pandas.DataFrame, feature: str,
            n: int) -> pandas.DataFrame:
        column_name = f'{feature}_{n}'
        prior_measurements = []
        for date in frame[feature].keys():
            prev_date = _decrement_years(date, n)
            for _ in range(self.years_insurance):
                if prev_date in self.weather_frame[feature]:
                    break
                prev_date = _decrement_years(prev_date)
            value = self.weather_frame[feature].get(prev_date)
            prior_measurements.append(value)
        frame[column_name] = prior_measurements
        return frame

    def _make_train_frame(self) -> pandas.DataFrame:
        train_frame = self.weather_frame.copy()
        return self._prepare_data_frame(train_frame)

    def _make_prediction_frame(self) -> pandas.DataFrame:
        prediction_frame = pandas.DataFrame(
            data=[
                utils.WeatherData(self.prediction_date, 0, 0, 0, 0, 0, 0, 0),
            ],
            columns=utils.WeatherData.get_fields(),
        ).set_index(self.index)
        return self._prepare_data_frame(prediction_frame)

    def _split_frame(
            self, frame: pandas.DataFrame, predict_feature: str = '',
    ) -> Tuple[pandas.DataFrame, Optional[pandas.Series]]:
        return frame[[
            column
            for column in frame.columns
            if column not in self.features
        ]],  frame.get(predict_feature)


def train_model_once(config: settings.Config):
    supervisor = Supervisor(config)
    supervisor.train()


def predict_weather_once(config: settings.Config):
    supervisor = Supervisor(config)
    supervisor.predict()


def _wx_input_fn(x, y=None, num_epochs=None, shuffle=True, batch_size=1300):
    return tensorflow.estimator.inputs.pandas_input_fn(
        x=x,
        y=y,
        num_epochs=num_epochs,
        shuffle=shuffle,
        batch_size=batch_size,
    )


def _decrement_years(date: datetime.date, years: int = 1) -> datetime.date:
    if date.month == 2 and date.day == 29 and years % 4 != 0:
        return datetime.date(date.year - years, 3, 1)
    return datetime.date(date.year - years, date.month, date.day)
