from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"

    # Cache TTL (in seconds)
    CACHE_TTL: int = 60 * 60 * 24  # 24 hours

    # Key Prefix
    CACHE_PREFIX: str = "site_profile"

    # Service Config
    SERVICE_NAME: str = "cache-service"
    DEBUG: bool = True

    # Pydantic V2 way of handling config
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra='ignore' # Prevents crashing if extra vars are in .env
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()