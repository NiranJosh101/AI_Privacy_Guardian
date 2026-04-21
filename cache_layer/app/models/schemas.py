from pydantic import BaseModel, Field
from typing import Any, Dict, Optional



class CacheSetRequest(BaseModel):
    domain: str = Field(..., example="twitter.com")
    site_profile: Dict[str, Any]



class CacheHitResponse(BaseModel):
    found: bool = True
    site_profile: Dict[str, Any]



class CacheMissResponse(BaseModel):
    found: bool = False
    site_profile: Optional[Dict[str, Any]] = None



class CacheResponse(BaseModel):
    found: bool
    site_profile: Optional[Dict[str, Any]] = None
    source: Optional[str] = None  # "cache" or "fresh"