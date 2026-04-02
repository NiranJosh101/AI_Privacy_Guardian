from typing import List, Optional, TypedDict, Dict, Annotated
import operator

class ExplorerState(TypedDict):
    base_url: str
    regulatory_map: Dict[str, List[Dict[str, any]]] 
    content_store: Annotated[Dict[str, str], operator.ior] 
    is_blocked: bool
    error_log: List[str]
    final_report: Optional[str]