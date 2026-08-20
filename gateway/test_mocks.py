from fastapi import FastAPI
from pydantic import BaseModel
import time

app = FastAPI(title="Privacy Guardian Mocks")



# --- MOCK JUDGE (Service 6) ---
@app.post("/v1/evaluate")
async def mock_judge(request: dict):
    print("⚖️ Judge: Evaluating logic...")
    # Simulate a violation find
    return {
        "verdict": "FLAG",
        "risk_score": 80,
        "explanation": "This site collects location data and shares it with brokers, which violates your 'Balanced' persona constraints.",
        "violations": [
            {
                "type": "Data Sharing",
                "severity": "critical",
                "description": "Third-party sharing is enabled with no opt-out."
            },
            {
                "type": "Data Retention",
                "severity": "warning",
                "description": "Data is retained for 2 years, which exceeds the 1-year limit."
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)