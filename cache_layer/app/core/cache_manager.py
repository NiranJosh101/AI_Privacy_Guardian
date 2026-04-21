import json
import redis.asyncio as redis
from typing import Optional, Dict, Any

# Pydantic V2 Fix: Move import to the correct utility path
from pydantic.json import pydantic_encoder 

from configs.config import settings
from utils.domain import normalize_domain


class CacheManager:
    def __init__(self):
        # Initializing the Async Connection Pool
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    def _make_key(self, domain: str) -> str:
        normalized = normalize_domain(domain)
        return f"{settings.CACHE_PREFIX}:{normalized}"

    async def get_site_profile(self, domain: str) -> Optional[Dict[str, Any]]:
        key = self._make_key(domain)
        try:
            # Await the async redis call
            data = await self.client.get(key)
            if not data:
                return None

            return json.loads(data)
        except Exception as e:
            # Cache failure must be silent (non-blocking)
            print(f"[CACHE ERROR - GET] {e}")
            return None

    async def set_site_profile(self, domain: str, site_profile: Dict[str, Any]) -> bool:
        key = self._make_key(domain)
        try:
            # Use pydantic_encoder to handle complex objects correctly
            serialized_data = json.dumps(
                site_profile, 
                default=pydantic_encoder
            )
            
            await self.client.setex(
                key,
                settings.CACHE_TTL,
                serialized_data
            )
            return True
        except Exception as e:
            print(f"[CACHE ERROR - SET] {e}")
            return False

    async def delete_site_profile(self, domain: str) -> bool:
        key = self._make_key(domain)
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            print(f"[CACHE ERROR - DELETE] {e}")
            return False

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except Exception:
            return False

    async def close(self):
        """Important for clean shutdowns in async apps"""
        await self.client.aclose() # Use aclose() for redis.asyncio