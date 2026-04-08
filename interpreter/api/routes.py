from fastapi import APIRouter, HTTPException, Depends
from engine.orchestrator import InterpreterOrchestrator
from models.request import PolicyRequest
from models.domain import SiteProfile
from utils.text_processor import get_orchestrator # Using your new utility path

router = APIRouter()

@router.post("/interpret", response_model=SiteProfile)
async def interpret_policy(
    request: PolicyRequest, 
    orchestrator: InterpreterOrchestrator = Depends(get_orchestrator)
):
    """
    Receives the ExplorerResponse structure, runs the RAG pipeline, 
    and returns a structured SiteProfile.
    """
    # Defensive Check: If Explorer couldn't get text, don't waste LLM tokens
    if not request.final_report or len(request.final_report) < 100:
        raise HTTPException(
            status_code=400, 
            detail="Policy text too short or empty. Cannot perform analysis."
        )

    try:
        # We use the helper property .domain and the .final_report field
        result = await orchestrator.interpret_policy(
            domain=request.domain, 
            raw_text=request.final_report
        )
        return result
    except Exception as e:
        # Log the error here in a real MLOps environment
        raise HTTPException(status_code=500, detail=f"Interpretation failed: {str(e)}")