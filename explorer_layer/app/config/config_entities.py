from pydantic import BaseModel, Field
from typing import List

class BrowserConfig(BaseModel):
    headless: bool
    user_agent: str
    timeout: int

class SearchDiscoveryConfig(BaseModel):
    max_links_to_analyze: int
    policy_keywords: List[str]

class AppConfig(BaseModel):
    browser: BrowserConfig = Field(alias="browser_settings")
    search: SearchDiscoveryConfig = Field(alias="search_discovery")