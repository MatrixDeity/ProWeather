import argparse
import datetime
import os

import xlrd

import utils


START_ROW = 7


def main():
    args = _parse_args()
    xls_path = os.path.abspath(args.target)
    target_path = os.path.join(os.getcwd(), 'xls_weather.pkl')
    book = xlrd.open_workbook(xls_path)
    sheet = book.sheet_by_index(0)
    rows_number = sheet.nrows

    weather_data = []
    i = START_ROW
    while i < rows_number:
        weather, diff = _process_all_dates(sheet, i)
        weather_data.append(weather)
        i += diff

    utils.dump_weather_data(weather_data, target_path)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='Path to xls file')
    return parser.parse_args()


def _slice_column(sheet, col, beg, count, default=None):
    if default is None:
        return [
            float(cell.value)
            for cell in sheet.col_slice(col, beg, beg + count)
            if type(cell.value) == float
        ]
    return [
        float(cell.value) if type(cell.value) == float else default
        for cell in sheet.col_slice(col, beg, beg + count)
    ]


def _column_mean(sheet, col, beg, count, default=None):
    values = _slice_column(sheet, col, beg, count, default=default)
    return float('{:.1f}'.format(sum(values) / len(values)))


def _column_max(sheet, col, beg, count, default=None):
    return max(_slice_column(sheet, col, beg, count, default=default))


def _column_min(sheet, col, beg, count, default=None):
    return min(_slice_column(sheet, col, beg, count, default=default))


def _column_sum(sheet, col, beg, count, default=None):
    return sum(_slice_column(sheet, col, beg, count, default=default))


def _process_all_dates(sheet, idx):
    i = idx
    date = datetime.datetime.strptime(
        sheet.cell(i, 0).value, '%d.%m.%Y %H:%M',
    ).date()
    count = 0
    while (i < sheet.nrows and
           datetime.datetime.strptime(
               sheet.cell(i, 0).value, '%d.%m.%Y %H:%M',
           ).date() == date):
        count += 1
        i += 1

    min_temp = _column_min(sheet, 1, idx, count)
    max_temp = _column_max(sheet, 1, idx, count)
    avg_temp = _column_mean(sheet, 1, idx, count)
    avg_pres = _column_mean(sheet, 3, idx, count)
    avg_humid = _column_mean(sheet, 5, idx, count)
    tot_precip = _column_sum(sheet, 23, idx, count, default=0.0)
    max_wind = _column_max(sheet, 7, idx, count)

    return utils.WeatherData(
        date=date,
        max_temp=max_temp,
        min_temp=min_temp,
        avg_temp=avg_temp,
        avg_pres=avg_pres,
        avg_humid=avg_humid,
        tot_precip=tot_precip,
        max_wind=max_wind,
    ), count


if __name__ == '__main__':
    main()
