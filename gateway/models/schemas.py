from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class PrivacyConstraints(BaseModel):
    no_sharing: bool = True
    no_tracking: bool = True
    no_fingerprinting: bool = False
    no_ads: bool = True
    max_retention_30: bool = True
    require_encryption: bool = True
    no_location: bool = False
    no_biometrics: bool = False

class UserPersona(BaseModel):
    userId: str
    persona: str 
    constraints: PrivacyConstraints


class ScanRequest(BaseModel):
    userId: str
    url: str

class ScanStage(str, Enum):
    IDLE = "idle"
    DISCOVERY = "discovery"  
    REASONING = "reasoning"    
    JUDGING = "judging"        
    COMPLETE = "complete"



class Violation(BaseModel):
    type: str         
    severity: str     
    description: str  

class ScanVerdict(BaseModel):
    verdict: str       # "FLAG" or "CLEAR"
    risk_score: int    # 0-100
    explanation: str
    violations: List[Violation] = []

class ScanStatusResponse(BaseModel):
    jobId: str
    status: ScanStage
    result: Optional[ScanVerdict] = None



class ExplorerResponse(BaseModel):
    base_url: str
    is_blocked: bool
    final_report: str
    error_log: list[str]



class SiteProfile(BaseModel):
    domain: str
    last_updated: Optional[str]
    data_collection: Dict[str, bool] = Field(
        description="Flags for: email, location, biometrics, usage_stats, etc."
    )
    third_party_sharing: bool
    sharing_details: List[str] = Field(default_factory=list, description="Names of partners or categories")
    data_retention_period: Optional[int] = Field(None, description="Retention in days, null if indefinite")
    encryption_standard: str # e.g., "TLS 1.3", "None", "AES-256"
    opt_out_available: bool
    last_updated: Optional[str]