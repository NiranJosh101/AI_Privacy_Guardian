from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


# 1. Define Request/Response Schemas
class ExploreRequest(BaseModel):
    url: str

class ExplorerResponse(BaseModel):
    base_url: str
    is_blocked: bool
    final_report: str
    error_log: List[str]