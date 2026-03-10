# configs/config_manager.py
import yaml
import os
import re
from configs.config_entities import MasterConfig

class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._config = cls._load_config()
        return cls._instance

    @staticmethod
    def _load_config() -> MasterConfig:
        path = "configs/config.yaml"
        
        # Regex to find ${VAR} or ${VAR:-default}
        pattern = re.compile(r'\$\{(\w+)(?::-(.*))?\}')

        def env_constructor(loader, node):
            value = node.value
            match = pattern.match(value)
            env_var, default = match.groups()
            return os.environ.get(env_var, default)

        yaml.add_implicit_resolver('!env', pattern, None)
        yaml.add_constructor('!env', env_constructor)

        with open(path, 'r') as f:
            raw_config = yaml.load(f, Loader=yaml.FullLoader)
            return MasterConfig(**raw_config)

    @property
    def values(self) -> MasterConfig:
        return self._config

# Global instance for easy access
cfg = ConfigManager().values