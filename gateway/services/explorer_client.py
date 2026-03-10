# services/explorer_client.py
import httpx
from models.schemas import ExplorerOutput
from configs.config_manager import cfg
from fastapi import HTTPException

class ExplorerClient:
    def __init__(self):
        self.url = cfg.services['explorer'].url
        self.timeout = cfg.services['explorer'].timeout # Usually 30s+

    async def discover_site_content(self, target_url: str) -> ExplorerOutput:
        """
        Sends the URL to the Explorer Service for LangGraph-based discovery.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.url}/explore",
                    json={"url": target_url},
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # Convert the Agent's output into our strict Schema
                return ExplorerOutput(**response.json())
                
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Explorer Service timed out during agentic search")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Explorer Error: {str(e)}")