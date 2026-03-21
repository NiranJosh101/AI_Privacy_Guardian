from typing import List, Optional, TypedDict, Dict, Annotated
import operator

class ExplorerState(TypedDict):
    # Input Data
    base_url: str
    
    # Discovery Data (The "Regulatory Map")
    # Category (Privacy, Terms, etc.) -> List of found URLs
    regulatory_map: Dict[str, List[Dict[str, any]]] 
    
    # Extraction Storage
    # URL -> Clean Markdown Content
    # Using operator.ior (a reducer) to indicate that this dictionary will be updated incrementally as new content is extracted.
    content_store: Annotated[Dict[str, str], operator.ior] 
    
    # Progress Tracking
    is_blocked: bool
    error_log: List[str]
    
    # Final Output
    final_report: Optional[str]