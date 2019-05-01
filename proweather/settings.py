import os
from typing import Optional

import yaml


class ConfigNotFound(FileNotFoundError):
    pass


class Config:
    def __init__(self, path: Optional[str] = None):
        config_path = path or os.path.join(os.getcwd(), 'config.yaml')
        try:
            with open(config_path, 'r') as config_file:
                config = yaml.load(config_file, Loader=yaml.Loader)
        except FileNotFoundError:
            raise ConfigNotFound(f'Config is not found ({config_path})')
        self.__dict__.update(config)
