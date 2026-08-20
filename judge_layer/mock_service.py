from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Judge Service Mock")


# --- MOCK JUDGE ---
@app.post("/v1/evaluate")
async def mock_evaluate(request: dict):
    # Log incoming request keys or domain if passed in context
    print("⚖️ Judge: Evaluating constraints against site profile...")

    # Happy path: Return CLEAR verdict with zero violations
    return {
        "verdict": "CLEAR",
        "risk_score": 100,
        "explanation": "Site profile satisfies all user privacy constraints. No violations detected.",
        "violations": []
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)