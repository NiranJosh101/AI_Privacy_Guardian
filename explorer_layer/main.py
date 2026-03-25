from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from app.agent.graph import explorer_agent
from app.models.schemas import ExploreRequest, ExploreResponse

app = FastAPI(
    title="Explorer Service",
    description="Agentic Web Discovery & Regulatory Document Extraction",
    version="1.0.0"
)




@app.post("/explore", response_model=ExploreResponse)
async def run_exploration(request: ExploreRequest):
    print(f"--- DEBUG: Received request for {request.url} ---") # ADD THIS
    
    initial_state = {
        "base_url": str(request.url),
        "regulatory_map": {},
        "content_store": {},
        "is_blocked": False,
        "error_log": [],
        "final_report": None
    }

    try:
        print("--- DEBUG: Starting Agent Invoke ---") # ADD THIS
        final_state = await explorer_agent.ainvoke(initial_state)
        print("--- DEBUG: Agent Finished ---") # ADD THIS
        
        return ExploreResponse(
            base_url=final_state.get("base_url", ""),
            is_blocked=final_state.get("is_blocked", False),
            final_report=final_state.get("final_report", ""),
            error_log=final_state.get("error_log", [])
        )
    
    except Exception as e:
        print(f"--- DEBUG: Caught Error: {e} ---") # ADD THIS
        raise HTTPException(status_code=500, detail=str(e))
    

# Health Check
@app.get("/health")
async def health():
    return {"status": "online", "service": "explorer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)