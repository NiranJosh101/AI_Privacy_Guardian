from pydantic import BaseModel, Field
from typing import List

class PolicyRequest(BaseModel):
    # Mapping Explorer's 'base_url' to our 'domain'
    base_url: str = Field(..., example="https://example.com")
    # Mapping Explorer's 'final_report' to our 'raw_text'
    final_report: str = Field(..., description="The full scraped text of the privacy policy")
    is_blocked: bool = False
    error_log: List[str] = []

    @property
    def domain(self) -> str:
        """Helper to extract clean domain from base_url for Pinecone namespaces."""
        return self.base_url.replace("https://", "").replace("http://", "").split('/')