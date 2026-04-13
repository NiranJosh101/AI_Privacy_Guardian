from fastapi import APIRouter, HTTPException
from ..models import PrivacyConstraints, SiteProfile, EvaluationResult
from ..core.judge import JudgeEngine

# Create the router
router = APIRouter(prefix="/v1", tags=["Evaluation"])

# Initialize the engine
judge = JudgeEngine()

@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate_privacy(constraints: PrivacyConstraints, site: SiteProfile):
    """
    Receives Site Reality + User Intent and returns a Privacy Verdict.
    """
    try:
        # Orchestration happens here
        result = judge.evaluate_site(constraints, site)
        return result
    except Exception as e:
        # In a real app, you'd log this with your logger
        raise HTTPException(status_code=500, detail="Internal Judge Logic Error")