import httpx
import re
from models.schemas import ExplorerOutput
from configs.config_manager import cfg
from fastapi import HTTPException

class ExplorerClient:
    def __init__(self):
        # 1. Get the raw value from the config manager
        raw_val = str(cfg.services['explorer'].url)
        
        # 2. If it contains the shell variable syntax, extract the fallback
        if ":-" in raw_val:
            # Extract everything between :- and the closing }
            # Then strip quotes and whitespace
            extracted = raw_val.split(":-")[-1].strip("}\"' ")
            self.url = extracted
        else:
            self.url = raw_val.strip("\"' ")

        # 3. Final Protocol Check
        if not self.url.startswith(('http://', 'https://')):
            self.url = f"http://{self.url}"
            
        self.timeout = cfg.services['explorer'].timeout
        # This will print to the console the MOMENT the gateway starts
        print(f"✅ ExplorerClient Initialized with URL: {self.url}")

    async def discover_site_content(self, target_url: str) -> ExplorerOutput:
        async with httpx.AsyncClient() as client:
            # Construct the endpoint
            endpoint = f"{self.url.rstrip('/')}/explore"
            
            try:
                print(f"📡 Requesting: {endpoint} | Target: {target_url}")
                
                response = await client.post(
                    endpoint,
                    json={"url": target_url},
                    timeout=self.timeout
                )
                response.raise_for_status()
                return ExplorerOutput(**response.json())
                
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Explorer Error at {endpoint}: {str(e)}"
                )