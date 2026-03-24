import yaml
from pathlib import Path
from app.config.config_entities import AppConfig 

class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
            # Path(__file__).parent is the 'app/config' folder
            config_path = Path(__file__).parent / "config.yaml"
            
            with open(config_path, "r") as f:
                raw_config = yaml.safe_load(f)
                self.config = AppConfig(**raw_config)

# Global access point
settings = ConfigManager().config