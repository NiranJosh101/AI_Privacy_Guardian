from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Cache TTL (in seconds)
    CACHE_TTL: int = 60 * 60 * 24  # 24 hours

    # Key Prefix (helps avoid collisions in shared Redis)
    CACHE_PREFIX: str = "site_profile"

    # Service Config
    SERVICE_NAME: str = "cache-service"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton (prevents reloading config everywhere)
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()