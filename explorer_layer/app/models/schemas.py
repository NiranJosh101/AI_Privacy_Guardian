from pydantic import BaseModel, Field
from typing import List, Optional

class ExploreRequest(BaseModel):
    url: str = Field(..., example="https://example.com")

class ExplorerResponse(BaseModel):
    base_url: str = Field(..., description="The cleaned target URL")
    is_blocked: bool = Field(default=False)
    # Use Optional and a default empty string
    final_report: Optional[str] = Field(default="") 
    # Use a default factory for lists to avoid 'None' issues
    error_log: List[str] = Field(default_factory=list)