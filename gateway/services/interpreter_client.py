import httpx
from models.schemas import SiteProfile, ExplorerResponse
from configs.config_manager import cfg
from fastapi import HTTPException


class InterpreterClient:
    def __init__(self):
        base_url = cfg.services['interpreter'].url
        
        # Strip any accidental quotes and check protocol
        base_url = base_url.strip().replace('"', '').replace("'", "")
        
        if not base_url.startswith(('http://', 'https://')):
            base_url = f"http://{base_url}"
            
        self.url = base_url
        self.timeout = cfg.services['interpreter'].timeout

    async def extract_site_profile(self, explorer_data: ExplorerResponse) -> SiteProfile:

        payload = {
            "domain": explorer_data.url,
            "content": explorer_data.raw_markdown,
            "extraction_targets": cfg.interpreter.extraction_targets
        }
        print(f"DEBUG: Sending to Interpreter: {payload}") 

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.url}/interpret",
                    json=payload,
                    timeout=self.timeout
                )

                response.raise_for_status()

                return SiteProfile(**response.json())

            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Interpreter Service timed out")

            except Exception as e:
                print(f"Interpretation Error: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to parse site privacy clauses")