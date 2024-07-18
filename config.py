import json
from pathlib import Path

class Config:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        config_path = Path(self.config_file)
        if not config_path.is_file():
            raise FileNotFoundError(f"Config file {self.config_file} not found.")
        
        with open(config_path) as f:
            config_data = json.load(f)
            self.data = config_data
            self.app_name = config_data.get("app_name")
            self.version = config_data.get("version")
            self.ehProd = config_data.get("ehProd")
            self.connections = config_data.get("connections")


config = Config("config.json")
