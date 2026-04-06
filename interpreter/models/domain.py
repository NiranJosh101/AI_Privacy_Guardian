from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class SiteProfile(BaseModel):
    """
    The 'Privacy DNA' of a website, extracted from its legal policies.
    This serves as the standardized contract for the Judge Service.
    """
    domain: str = Field(..., description="The root domain of the site (e.g., example.com)")
    
    # Nested Dict for granular collection flags
    data_collection: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email": False,
            "location": False,
            "biometrics": False,
            "usage_stats": False,
            "financial_info": False
        },
        description="True/False flags for specific data types mentioned in the policy."
    )
    
    third_party_sharing: bool = Field(
        ..., 
        description="Whether the site explicitly shares data with non-affiliated third parties."
    )
    
    sharing_details: List[str] = Field(
        default_factory=list, 
        description="Names or categories of partners mentioned (e.g., 'Google Analytics', 'AdRoll')."
    )
    
    data_retention_period: Optional[int] = Field(
        None, 
        description="Storage duration in days. Null if indefinite or not stated."
    )
    
    encryption_standard: str = Field(
        "None", 
        description="The highest security standard mentioned (e.g., 'TLS 1.3', 'AES-256')."
    )
    
    opt_out_available: bool = Field(
        False, 
        description="Is there a clear mechanism for users to opt-out of tracking or data sales?"
    )

    last_updated: Optional[str] = Field(
        None, 
        description="The 'Effective Date' found in the policy document."
    )