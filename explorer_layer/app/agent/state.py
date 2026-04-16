from typing import List, Optional, TypedDict, Dict, Annotated
import operator

class ExplorerState(TypedDict):
    base_url: str
    regulatory_map: Annotated[Dict[str, List[Dict]], operator.ior]
    content_store: Annotated[Dict[str, str], operator.ior] 
    is_blocked: bool
    error_log: Annotated[List[str], operator.add]
    final_report: Optional[str]