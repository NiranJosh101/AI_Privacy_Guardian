import httpx
import re
from models.schemas import ExplorerResponse
from configs.config_manager import cfg
from fastapi import HTTPException

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
       
        print(f"✅ ExplorerClient Initialized with URL: {self.url}")


    async def discover_site_content(self, target_url: str) -> ExplorerResponse:
        async with httpx.AsyncClient() as client:
            endpoint = f"{self.url.rstrip('/')}/explore"
            
            try:
                # 1. Use a generous timeout for the scraper
                response = await client.post(
                    endpoint,
                    json={"url": target_url},
                    timeout=120.0 # 2 minutes for deep scraping
                )
                
                # 2. DEBUG: See exactly what the Explorer sent back
                print(f"DEBUG: Explorer raw response: {response.text[:200]}...")
                
                response.raise_for_status()
                
                # 3. Return the raw dict first if you suspect Pydantic is crashing
                data = response.json()
                return ExplorerResponse(**data)
                
            except httpx.HTTPStatusError as e:
                # This captures the 500s coming FROM the Explorer
                print(f"Explorer logic failed: {e.response.text}")
                raise HTTPException(status_code=500, detail="Explorer service encountered a logic error.")
            except Exception as e:
                # This captures connection issues or Pydantic validation crashes
                print(f"Gateway connection/validation error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to bridge to Explorer: {str(e)}")