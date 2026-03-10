import httpx
from models.schemas import SiteProfile, ExplorerOutput
from configs.config_manager import cfg
from fastapi import HTTPException


class InterpreterClient:
    def __init__(self):
        self.url = cfg.services['interpreter'].url
        self.timeout = cfg.services['interpreter'].timeout

    async def extract_site_profile(self, explorer_data: ExplorerOutput) -> SiteProfile:

        payload = {
            "domain": explorer_data.url,
            "content": explorer_data.raw_markdown,
            "extraction_targets": cfg.interpreter.extraction_targets
        }

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