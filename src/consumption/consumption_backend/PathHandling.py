# Initializing config file location
from pathlib import Path
import json

DEFAULT_CONFIG = {
    "DB_PATH" : "~/Consumption/consumption.db"
}

CONSUMPTION_PATH = Path.home() / "Consumption"
CONFIG_PATH = CONSUMPTION_PATH / "config.json"

def setup_config():
    if not CONFIG_PATH.is_file():
        CONSUMPTION_PATH.mkdir(exist_ok=True)
        with open(CONFIG_PATH, "w+") as f:
            json.dump(DEFAULT_CONFIG, f)