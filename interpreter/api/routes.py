from fastapi import APIRouter, HTTPException, Depends
from engine.orchestrator import InterpreterOrchestrator
from engine.config_manager import ConfigManager
from models.request import PolicyRequest
from models.domain import SiteProfile

router = APIRouter()

# Singleton-style config management
def get_orchestrator():
    config_manager = ConfigManager()
    return InterpreterOrchestrator(config_manager)

@router.post("/interpret", response_model=SiteProfile)
async def interpret_policy(
    request: PolicyRequest, 
    orchestrator: InterpreterOrchestrator = Depends(get_orchestrator)
):
    """
    Receives raw policy text, runs the RAG pipeline, 
    and returns a structured SiteProfile.
    """
    try:
        # We pass the domain and the text to the orchestrator
        result = await orchestrator.interpret_policy(
            domain=request.domain, 
            raw_text=request.raw_text
        )
        return result
    except Exception as e:
        # Standardized error reporting for the Gateway
        raise HTTPException(status_code=500, detail=f"Interpretation failed: {str(e)}")