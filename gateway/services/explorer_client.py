import httpx
import re
from models.schemas import ExplorerOutput
from configs.config_manager import cfg
from fastapi import HTTPException

class ExplorerClient:
    def __init__(self):
        raw_url = cfg.services['explorer'].url
        
        # 1. Resolve potential shell-style defaults if the parser failed
        # This regex looks for the URL inside ${VAR:-"URL"}
        match = re.search(r':-"?([^"}]*)"?\}', raw_url)
        if match:
            self.url = match.group(1)
        else:
            self.url = raw_url

        # 2. Defensive Protocol Check
        if not self.url.startswith(('http://', 'https://')):
            self.url = f"http://{self.url}"
            
        self.timeout = cfg.services['explorer'].timeout

    async def discover_site_content(self, target_url: str) -> ExplorerOutput:
        async with httpx.AsyncClient() as client:
            try:
                # This log will tell you EXACTLY what it resolved to
                print(f"📡 ExplorerClient calling: {self.url}/explore")
                
                response = await client.post(
                    f"{self.url}/explore",
                    json={"url": target_url},
                    timeout=self.timeout
                )
                response.raise_for_status()
                return ExplorerOutput(**response.json())
                
            except Exception as e:
                # Inclusion of self.url here makes debugging the next fail much easier
                raise HTTPException(
                    status_code=500, 
                    detail=f"Explorer Error calling {self.url}: {str(e)}"
                )