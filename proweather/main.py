import sys

import application


class BadPythonVersion(EnvironmentError):
    pass


def main():
    if sys.version_info < (3, 7):
        raise BadPythonVersion('ProWeather requires Python 3.7+')

    application.Application().run()


if __name__ == '__main__':
    main()
