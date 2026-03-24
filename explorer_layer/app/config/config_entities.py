from pydantic import BaseModel, Field
from typing import Dict, List

class BrowserConfig(BaseModel):
    headless: bool
    user_agent: str
    timeout: int

class SearchDiscoveryConfig(BaseModel):
    document_categories: Dict[str, List[str]]
    max_links_to_analyze: int = 20

class AppConfig(BaseModel):
    browser: BrowserConfig = Field(alias="browser_settings")
    search: SearchDiscoveryConfig = Field(alias="search_discovery")

    class Config:
        populate_by_name = True