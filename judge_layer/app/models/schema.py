from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, timezone

class PrivacyConstraints(BaseModel):
    """The 'Intent' - What the user wants to avoid or require."""
    no_sharing: bool = False
    no_tracking: bool = False
    no_fingerprinting: bool = False
    no_ads: bool = False
    max_retention_30: bool = False
    require_encryption: bool = False
    no_location: bool = False
    no_biometrics: bool = False


class SiteProfile(BaseModel):
    domain: str
    last_updated: Optional[str]
    # Keep the dict to match Interpreter's output exactly
    data_collection: Dict[str, bool] = Field(
        description="Flags for: email, location, biometrics, usage_stats, etc."
    )
    third_party_sharing: bool
    sharing_details: List[str] = Field(default_factory=list)
    data_retention_period: Optional[int] = Field(None)
    encryption_standard: str # e.g., "TLS 1.3", "None", "AES-256"
    opt_out_available: bool

# class Violation(BaseModel):
#     """The result of a single Rule evaluation."""
#     constraint_key: str
#     severity: str # critical, warning, info
#     message: str
#     actual_value: Optional[str | int | bool] = None


# class EvaluationResult(BaseModel):
#     """The final response from the Judge Service."""
#     domain: str
#     score: int
#     violations: List[dict] # Or List[Violation] if defined above
#     summary: str
    
#     # We use the 'datetime' class here, and a lambda for the default
#     timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Violation(BaseModel):
    type: str         
    severity: str     
    description: str  

class EvaluationResult(BaseModel):
    verdict: str       # "FLAG" or "CLEAR"
    risk_score: int    # 0-100
    explanation: str
    violations: List[Violation] = []



class ConstraintKeys:
    NO_SHARING = "no_sharing"
    NO_TRACKING = "no_tracking"
    NO_FINGERPRINTING = "no_fingerprinting"
    NO_ADS = "no_ads"
    MAX_RETENTION_30 = "max_retention_30"
    REQUIRE_ENCRYPTION = "require_encryption"
    NO_LOCATION = "no_location"
    NO_BIOMETRICS = "no_biometrics"   