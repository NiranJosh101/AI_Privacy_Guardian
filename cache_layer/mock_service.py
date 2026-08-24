from fastapi import FastAPI, Query
import uvicorn

app = FastAPI(title="Cache Service Mock")


# Matches: GET /cache/site-profile?domain=https%3A%2F%2Fchowdeck.com%2F
@app.get("/cache/site-profile")
async def mock_get_cache(domain: str = Query(...)):
    print(f"💾 Cache GET MISS for domain: {domain}")

    # Return a cache miss so the gateway executes the full Explorer -> Interpreter -> Judge pipeline
    return {
        "found": False,
        "site_profile": None,
        "source": "miss"
    }


@app.post("/cache/site-profile")
async def mock_set_cache(request: dict):
    print(f"💾 Cache SET for domain: {request.get('domain')}")
    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)