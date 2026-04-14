import httpx
from models.schemas import SiteProfile, ScanVerdict, PrivacyConstraints
from configs.config_manager import cfg
from fastapi import HTTPException

class JudgeClient:
    def __init__(self):
        # Clean the URL from config to handle potential quotes/whitespace
        raw_url = cfg.services['judge'].url
        clean_url = raw_url.strip().replace('"', '').replace("'", "")

        if not clean_url.startswith(('http://', 'https://')):
            clean_url = f"http://{clean_url}"

        self.url = clean_url
        self.timeout = cfg.services['judge'].timeout

    async def generate_verdict(
        self,
        constraints: PrivacyConstraints, # This is the 'persona' passed from scan.py
        site_profile: SiteProfile
    ) -> ScanVerdict:

        # We wrap these in keys so the Service can use Body(embed=True)
        payload = {
            "constraints": constraints.dict(),
            "site": site_profile.dict()
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.url}/v1/evaluate",
                    json=payload,
                    timeout=self.timeout
                )

                response.raise_for_status()
                
                # IMPORTANT: ScanVerdict must have identical fields to 
                # the Service's EvaluationResult
                return ScanVerdict(**response.json())

            except httpx.HTTPStatusError as e:
                # Captures 4xx or 5xx errors from the service
                raise HTTPException(status_code=e.response.status_code, detail=f"Judge Service Error: {e.response.text}")
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Judge Service is unreachable")