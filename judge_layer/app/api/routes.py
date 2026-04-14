from fastapi import APIRouter, HTTPException, Body
from app.models.schema import PrivacyConstraints, SiteProfile, EvaluationResult
from app.core.judge import JudgeEngine

router = APIRouter(prefix="/v1", tags=["Evaluation"])
judge = JudgeEngine()

@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate_privacy(
    # Body(embed=True) maps the "constraints" key in JSON to this parameter
    constraints: PrivacyConstraints = Body(embed=True), 
    # Body(embed=True) maps the "site" key in JSON to this parameter
    site: SiteProfile = Body(embed=True)
):
    """
    Receives Site Reality + User Intent and returns a Privacy Verdict.
    """
    try:
        # Pass the unpacked models into your logic engine
        result = judge.evaluate_site(constraints, site)
        return result
    except Exception as e:
        # Log the error for internal debugging
        print(f"Logic Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Judge Logic Error")