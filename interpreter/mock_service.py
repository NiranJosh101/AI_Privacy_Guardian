import asyncio
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Privacy DNA Service Mock")

# Add the route your client is actually calling
@app.post("/api/v1/interpret")
@app.post("/v1/profile")
async def mock_extract_profile(request: dict):
    base_url = request.get("base_url", "https://example.com")
    clean_domain = base_url.replace("https://", "").replace("http://", "").split('/')[0]

    print(f"🧬 Processing policy for: {clean_domain}")

    # Non-blocking delay
    await asyncio.sleep(5)

    return {
        "domain": clean_domain,
        "data_collection": {
            "email": True,
            "location": True,
            "biometrics": False,
            "usage_stats": True,
            "financial_info": False
        },
        "third_party_sharing": True,
        "sharing_details": ["Google Analytics", "AdRoll"],
        "data_retention_period": 730,
        "encryption_standard": "TLS 1.3",
        "opt_out_available": False,
        "last_updated": "2026-01-15"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)