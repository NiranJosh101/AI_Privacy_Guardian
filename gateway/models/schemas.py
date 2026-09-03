import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ==========================================
# Legacy & API Interface Schemas
# ==========================================

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
    DISCOVERY = "discovery"      # Discovery Agent
    EXTRACTION = "extraction"    # Extractor Agent
    VERIFICATION = "verification"# Expert Agent
    JUDGING = "judging"          # Compliance Agent
    COMPLETE = "complete"
    FAILED = "failed"

class Violation(BaseModel):
    type: str         
    severity: str     
    description: str  
    source_clause: Optional[str] = None

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
    error_log: List[str] = []

# ==========================================
# Multi-Agent Domain & State Schemas
# ==========================================

class PolicyDocument(BaseModel):
    doc_type: str  # e.g., "Privacy Policy", "Cookie Policy", "Terms of Service"
    url: str
    raw_content_hash: str
    content: Optional[str] = None  # Wiped post-extraction during compaction

class ExtractedFact(BaseModel):
    category: str  # e.g., "Data Collection", "Third-Party Sharing", "Retention"
    clause_text: str
    source_url: str
    confidence_score: float = 1.0

class SiteProfile(BaseModel):
    domain: str
    discovered_policies: List[PolicyDocument] = Field(default_factory=list)
    extracted_facts: List[ExtractedFact] = Field(default_factory=list)
    data_collection: Dict[str, bool] = Field(default_factory=dict)
    third_party_sharing: bool = False
    sharing_details: List[str] = Field(default_factory=list)
    data_retention_period: Optional[int] = None
    encryption_standard: str = "Unknown"
    opt_out_available: bool = False
    last_updated: Optional[str] = None

class ExpertVerificationResult(BaseModel):
    is_valid: bool
    faithfulness_score: float
    feedback: Optional[str] = None
    unsupported_claims: List[str] = Field(default_factory=list)

class PrivacyGuardianState(BaseModel):
    """
    Global state managed by the LangGraph Orchestrator across sub-agent microservices.
    """
    job_id: str
    user_persona: Optional[UserPersona] = None
    site_profile: SiteProfile
    current_stage: ScanStage = ScanStage.IDLE
    retry_count: int = 0
    max_retries: int = 3
    verdict: Optional[ScanVerdict] = None
    
    # Scratchpad holds temporary payloads (DOM dumps, raw extraction responses)
    # Excluded from persistent state serialization via compaction
    node_scratchpad: Dict[str, Any] = Field(default_factory=dict)