import httpx
from typing import Optional, Dict, Any
from configs.config_manager import cfg
from fastapi import HTTPException
from models.schemas import SiteProfile

class CacheClient:
    def __init__(self):
        # 1. Standardize URL extraction (Matching ExplorerClient logic)
        raw_val = str(cfg.services['cache'].url)
        
        if ":-" in raw_val:
            self.base_url = raw_val.split(":-")[-1].strip("}\"' ")
        else:
            self.base_url = raw_val.strip("\"' ")

        if not self.base_url.startswith(('http://', 'https://')):
            self.base_url = f"http://{self.base_url}"

        # 2. Setup persistent client with the same limits as your other layers
        self.client = httpx.AsyncClient(
            base_url=self.base_url.rstrip('/'),
            timeout=5.0,  # Slightly higher than 2.0 to avoid race conditions
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
        print(f"✅ CacheClient Initialized with URL: {self.base_url}")

    async def get(self, domain: str) -> Optional[SiteProfile]: # 👈 Updated Type Hint
        endpoint = "/cache/site-profile"
        try:
            response = await self.client.get(endpoint, params={"domain": domain})
            
            if response.status_code == 404:
                return None
                
            response.raise_for_status()
            data = response.json()
            
            # 1. Extract the dict
            profile_dict = data.get("site_profile")
            
            # 2. Only attempt to instantiate if we actually have data
            if data.get("found") and profile_dict:
                return SiteProfile(**profile_dict) # 🚀 Returns a model, logic is happy
                
            return None
            
        except Exception as e:
            print(f"Gateway connection/validation error (Cache GET): {str(e)}")
            return None
        
        
    async def set(self, domain: str, site_profile: Any) -> bool:
        try:
            # 1. Safely convert to dict only if it's a Pydantic model
            # Use model_dump for Pydantic V2, dict() for V1
            if hasattr(site_profile, "model_dump") and callable(site_profile.model_dump):
                data = site_profile.model_dump()
            elif hasattr(site_profile, "dict") and callable(site_profile.dict):
                data = site_profile.dict()
            else:
                # It's already a dict or a basic type
                data = site_profile

            payload = {
                "domain": domain, 
                "site_profile": data
            }
            
            # 2. Make the request to the /cache prefix
            res = await self.client.post("/cache/site-profile", json=payload)
            return res.status_code == 200
            
        except Exception as e:
            print(f"[CacheClient SET Error] {e}")
            return False

    async def close(self):
        """Must be called on app shutdown to clean up the pool"""
        await self.client.aclose()