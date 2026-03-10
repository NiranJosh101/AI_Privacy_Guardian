# services/judge_client.py
import httpx
from models.schemas import UserPersona, SiteProfile, ScanVerdict
from configs.config_manager import cfg
from fastapi import HTTPException

class JudgeClient:
    def __init__(self):
        self.url = cfg.services['judge'].url
        self.timeout = cfg.services['judge'].timeout # Should be fast (~5s)

    async def generate_verdict(self, persona: UserPersona, site_profile: SiteProfile) -> ScanVerdict:
        """
        Sends the user persona and site profile to the Judge Service 
        for a deterministic rule-based comparison and risk scoring.
        """
        payload = {
            "persona": persona.dict(),
            "site_profile": site_profile.dict()
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.url}/judge",
                    json=payload,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                
                # Returns the final "FLAG" or "CLEAR" result for the Dashboard
                return ScanVerdict(**response.json())

            except httpx.RequestError as exc:
                print(f"Connection to Judge Service failed: {exc}")
                raise HTTPException(status_code=503, detail="Judge Service is offline")
            except Exception as e:
                print(f"Decision Error: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to generate privacy verdict")