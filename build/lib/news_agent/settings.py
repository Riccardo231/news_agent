#!/usr/bin/env python

import configparser
from pathlib import Path

def load_settings(config_file=None):
    config_file = config_file or Path(__file__).parent / "settings.ini"
    cp = configparser.ConfigParser()
    cp.read(config_file)
    return cp['DEFAULT']

def save_settings(settings, config_file=None):
    config_file = config_file or Path(__file__).parent / "settings.ini"
    cp = configparser.ConfigParser()
    cp["DEFAULT"] = dict(settings)
    with open(config_file, "w") as f:
        cp.write(f)