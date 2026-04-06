import yaml
from pathlib import Path
from .config_entities import InterpreterConfig, ChunkingConfig, EmbeddingConfig, VectorDBConfig

class ConfigManager:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._read_yaml()

    def _read_yaml(self) -> dict:
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def get_interpreter_config(self) -> InterpreterConfig:
        conf = self.config["interpreter"]
        return InterpreterConfig(
            chunking=ChunkingConfig(**conf["chunking"]),
            embeddings=EmbeddingConfig(**conf["embeddings"]),
            vector_db=VectorDBConfig(**conf["vector_db"])
        )