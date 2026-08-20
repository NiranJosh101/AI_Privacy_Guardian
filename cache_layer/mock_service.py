from fastapi import FastAPI, Query
from typing import Optional
import uvicorn

app = FastAPI(title="Cache Service Mock")


# Matches: GET /cache/site-profile?domain=https%3A%2F%2Fchowdeck.com%2F
@app.get("/cache/site-profile")
async def mock_get_cache(domain: str = Query(...)):
    print(f"💾 Cache GET hit for domain: {domain}")

    # Return 404 if you want to test cache misses, or hit payload below:
    return {
        "found": True,
        "source": "cache",
        "site_profile": {
            "domain": "chowdeck.com",
            "data_collection": {
                "email": True,
                "location": True,
                "biometrics": False,
                "usage_stats": True,
                "financial_info": True
            },
            "third_party_sharing": False,
            "sharing_details": [],
            "data_retention_period": 365,
            "encryption_standard": "TLS 1.3",
            "opt_out_available": True,
            "last_updated": "2026-01-15"
        }
    }


@app.post("/cache/site-profile")
async def mock_set_cache(request: dict):
    print(f"💾 Cache SET for domain: {request.get('domain')}")
    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)