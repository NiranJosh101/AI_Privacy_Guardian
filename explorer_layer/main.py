import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from app.agent.graph import explorer_agent
from app.models.schemas import ExploreRequest, ExplorerResponse
from telemetry import init_telemetry


app = FastAPI(
    title="Explorer Service",
    description="Agentic Web Discovery & Regulatory Document Extraction",
    version="1.0.0"
)

init_telemetry(app, "privacy-guardian-explorer")

@app.post("/explore", response_model=ExplorerResponse)
async def run_exploration(request: ExploreRequest):
    print(f"--- DEBUG: Received request for {request.url} ---")
    
    initial_state = {
        "base_url": str(request.url), # Your Graph internal key
        "regulatory_map": {},
        "content_store": {},
        "is_blocked": False,
        "error_log": [],
        "final_report": "" # Start with empty string to avoid None issues
    }

    try:
        print("--- DEBUG: Starting Agent Invoke ---")
        final_state = await explorer_agent.ainvoke(initial_state)
        print("--- DEBUG: Agent Finished ---")
        
        # KEY FIX: Mapping internal base_url to Schema base_url
        return ExplorerResponse(
            base_url=str(final_state.get("base_url", "")),
            is_blocked=bool(final_state.get("is_blocked", False)),
            final_report=str(final_state.get("final_report") or ""),
            error_log=list(final_state.get("error_log") or [])
        )
    
    except Exception as e:
        print(f"--- DEBUG: Caught Error: {e} ---")
        raise HTTPException(status_code=500, detail=str(e)) 

# Health Check
@app.get("/health")
async def health():
    return {"status": "online", "service": "explorer"}



if __name__ == "__main__":
    import uvicorn
    import sys
    import asyncio

    # CRITICAL WINDOWS FIX:
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    uvicorn.run(app, host="0.0.0.0", port=8004)