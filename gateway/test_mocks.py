from fastapi import FastAPI
from pydantic import BaseModel
import time

app = FastAPI(title="Privacy Guardian Mocks")

# --- MOCK EXPLORER (Service 4) ---
@app.post("/explore")
async def mock_explorer(request: dict):
    # Get the URL and clean it thoroughly
    raw_url = request.get("url").strip()
    
    return {
        "url": raw_url, 
        "page_title": "Example Tech Policy",
        "raw_markdown": "# Privacy Policy\nWe collect data.",
        "found_legal_links": [],
        "crawl_depth": 1,
        "status": "success"
    }


# --- MOCK INTERPRETER (Service 5) ---
@app.post("/interpret")
async def mock_interpreter(request: dict):
    print(f"🧠 Interpreter: Reasoning over content from {request.get('domain')}...")
    time.sleep(1.5) # Simulate RAG delay
    return {
        "domain": request.get("domain"),
        "last_updated": "2024-01-01",
        "data_collection": {"email": True, "location": True, "usage_stats": True},
        "third_party_sharing": True,
        "sharing_details": ["Ad-networks", "Data-Brokers"],
        "data_retention_period": 730,
        "encryption_standard": "TLS 1.2",
        "opt_out_available": False
    }

# --- MOCK JUDGE (Service 6) ---
@app.post("/judge")
async def mock_judge(request: dict):
    print("⚖️ Judge: Evaluating logic...")
    # Simulate a violation find
    return {
        "verdict": "FLAG",
        "risk_score": 90,
        "explanation": "This site collects location data and shares it with brokers, which violates your 'Balanced' persona constraints.",
        "violations": [
            {
                "type": "Data Sharing",
                "severity": "High",
                "description": "Third-party sharing is enabled with no opt-out."
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)