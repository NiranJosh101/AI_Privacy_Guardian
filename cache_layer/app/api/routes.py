from fastapi import APIRouter, Query
from app.core.cache_manager import CacheManager
from app.models.schemas import CacheSetRequest

router = APIRouter()
cache = CacheManager()

# -----------------------------
# GET: Retrieve SiteProfile
# -----------------------------
@router.get("/site-profile")
async def get_site_profile(domain: str = Query(..., description="Target domain")):
    # Must await the async manager
    cached = await cache.get_site_profile(domain)

    if cached:
        return {
            "found": True,
            "source": "cache",
            "site_profile": cached
        }

    return {
        "found": False,
        "source": "cache",
        "site_profile": None
    }

# -----------------------------
# POST: Store SiteProfile
# -----------------------------
@router.post("/site-profile")
async def set_site_profile(payload: CacheSetRequest):
    # Must await the async manager
    success = await cache.set_site_profile(
        domain=payload.domain,
        site_profile=payload.site_profile
    )

    return {
        "stored": success,
        "domain": payload.domain
    }

@router.delete("/site-profile")
async def delete_site_profile(domain: str = Query(...)):
    success = await cache.delete_site_profile(domain)
    return {
        "deleted": success,
        "domain": domain
    }

@router.get("/health")
async def health_check():
    # Must await the ping
    is_alive = await cache.ping()
    return {
        "status": "ok",
        "redis": is_alive
    }