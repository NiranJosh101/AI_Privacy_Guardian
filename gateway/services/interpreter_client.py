import httpx
from models.schemas import SiteProfile, ExplorerResponse
from configs.config_manager import cfg
from fastapi import HTTPException


class InterpreterClient:
    def __init__(self):
        # 1. Ensure we have a string and strip quotes
        raw_url = str(cfg.services['interpreter'].url).strip("\"' ")
        
        # 2. Add protocol if missing
        if not raw_url.startswith(('http://', 'https://')):
            raw_url = f"http://{raw_url}"
            
        # 3. Store base URL (we'll rstrip inside the method to be safe)
        self.url = raw_url
        self.timeout = cfg.services['interpreter'].timeout
        
        print(f"InterpreterClient Initialized at: {self.url}")

    async def extract_site_profile(self, explorer_data: ExplorerResponse) -> SiteProfile:
        # 1. Map the ExplorerResponse fields EXACTLY to the PolicyRequest model
        payload = {
            "base_url": explorer_data.base_url,
            "final_report": explorer_data.final_report,
            "is_blocked": explorer_data.is_blocked,
            "error_log": explorer_data.error_log
        }
        
        print(f"DEBUG: Sending to Interpreter: {self.url}/api/v1/interpret") 

        async with httpx.AsyncClient() as client:
            try:
                # 2. Add /api/v1 to the URL
                response = await client.post(
                    f"{self.url}/api/v1/interpret",
                    json=payload,
                    timeout=self.timeout
                )

                # This will help you see the 422 errors if they happen
                if response.status_code == 422:
                    print(f"SCHEMA ERROR: {response.json()}")

                response.raise_for_status()
                return SiteProfile(**response.json())

            except httpx.HTTPStatusError as e:
                print(f"HTTP Error {e.response.status_code}: {e.response.text}")
                raise HTTPException(status_code=e.response.status_code, detail="Interpreter communication failed")
            