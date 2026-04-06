from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class EmbeddingConfig:
    model_name: str

@dataclass(frozen=True)
class VectorDBConfig:
    index_name: str
    environment: str
    dimension: int
    metric: str

@dataclass(frozen=True)
class ChunkingConfig:
    chunk_size: int
    chunk_overlap: int
    separators: List[str]

@dataclass(frozen=True)
class InterpreterConfig:
    chunking: ChunkingConfig
    embeddings: EmbeddingConfig
    vector_db: VectorDBConfig 