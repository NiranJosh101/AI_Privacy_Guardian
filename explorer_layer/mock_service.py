import asyncio
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Explorer Service Mock")


@app.post("/explore")
@app.post("/v1/explore")
async def mock_explore(request: dict):
    raw_url = request.get("url", request.get("base_url", "https://example.com"))
    print(f"🔍 Explorer: Scraping {raw_url}")

    # Non-blocking 10-second delay
    await asyncio.sleep(7)

    return {
        "base_url": raw_url,
        "is_blocked": False,
        "final_report": (
            "PRIVACY POLICY\n"
            "We collect email addresses and location data for delivery optimization. "
            "Data is encrypted using TLS 1.3 and retained for 365 days."
        ),
        "error_log": []
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)