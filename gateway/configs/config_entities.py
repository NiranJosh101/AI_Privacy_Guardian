from pydantic import BaseModel
from typing import Dict, List


class ServiceConfig(BaseModel):
    url: str
    timeout: float


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int


class AppConfig(BaseModel):
    name: str
    version: str
    env: str



class InterpreterConfig(BaseModel):
    extraction_targets: List[str]


class MasterConfig(BaseModel):
    app: AppConfig
    services: Dict[str, ServiceConfig]
    redis: RedisConfig
    interpreter: InterpreterConfig  # NEW
    db_url: str  


