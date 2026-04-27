import httpx
import re
from models.schemas import ExplorerResponse
from configs.config_manager import cfg
from fastapi import HTTPException
import os


MOCK = os.getenv("MOCK_SERVICES", "false").lower() == "true"

class ExplorerClient:
    def __init__(self):
        
        raw_val = str(cfg.services['explorer'].url)
        
        if ":-" in raw_val:
            extracted = raw_val.split(":-")[-1].strip("}\"' ")
            self.url = extracted
        else:
            self.url = raw_val.strip("\"' ")

       
        if not self.url.startswith(('http://', 'https://')):
            self.url = f"http://{self.url}"
            
        self.timeout = cfg.services['explorer'].timeout
       
        print(f"ExplorerClient Initialized with URL: {self.url}")


    async def discover_site_content(self, target_url: str) -> ExplorerResponse:
    
        # MOCK PATH (this is what we're adding)
        if MOCK:
            print("ExplorerClient running in MOCK mode")

            mock_data = {
                "base_url": target_url,
                "is_blocked": True,
                "final_report": "Testing complete",
                "error_log": "Testing complete"
            }

            return ExplorerResponse(**mock_data)

        # REAL PATH (your existing code stays the same)
        async with httpx.AsyncClient() as client:
            endpoint = f"{self.url.rstrip('/')}/explore"
            
            try:
                response = await client.post(
                    endpoint,
                    json={"url": target_url},
                    timeout=120.0
                )
                
                print(f"DEBUG: Explorer raw response: {response.text[:200]}...")
                
                response.raise_for_status()
                
                data = response.json()
                return ExplorerResponse(**data)
                
            except httpx.HTTPStatusError as e:
                print(f"Explorer logic failed: {e.response.text}")
                raise HTTPException(status_code=500, detail="Explorer service encountered a logic error.")
            except Exception as e:
                print(f"Gateway connection/validation error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to bridge to Explorer: {str(e)}")