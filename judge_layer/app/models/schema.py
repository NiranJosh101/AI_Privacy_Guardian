from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

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

class Violation(BaseModel):
    """The result of a single Rule evaluation."""
    constraint_key: str
    severity: str # critical, warning, info
    message: str
    actual_value: Optional[str | int | bool] = None

class EvaluationResult(BaseModel):
    """The final response from the Judge Service."""
    domain: str
    score: int
    violations: List[Violation]
    summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)