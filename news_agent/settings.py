#!/usr/bin/env python

import configparser
from pathlib import Path

def load_settings(config_file=None):
    if config_file is None:
        # Cerca il file settings.ini in diversi percorsi
        possible_paths = [
            Path(__file__).parent / "settings.ini",  # Percorso relativo al modulo
            Path.cwd() / "news_agent" / "settings.ini",  # Percorso dalla directory corrente
            Path.home() / ".news_agent" / "settings.ini",  # Percorso home
        ]
        
        # Usa il primo file che esiste e ha una serpapi_key non vuota
        for path in possible_paths:
            if path.exists():
                cp = configparser.ConfigParser()
                cp.read(path)
                if 'DEFAULT' in cp and cp['DEFAULT'].get('serpapi_key', '').strip():
                    config_file = path
                    break
        
        # Se non troviamo un file con serpapi_key, usa il primo disponibile
        if config_file is None:
            for path in possible_paths:
                if path.exists():
                    config_file = path
                    break
    
    cp = configparser.ConfigParser()
    cp.read(config_file)
    return cp['DEFAULT']

def save_settings(settings, config_file=None):
    config_file = config_file or Path(__file__).parent / "settings.ini"
    cp = configparser.ConfigParser()
    cp["DEFAULT"] = dict(settings)
    with open(config_file, "w") as f:
        cp.write(f)