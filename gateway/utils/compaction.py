import logging
from models.schemas import PrivacyGuardianState

logger = logging.getLogger(__name__)

def compact_state(state: PrivacyGuardianState) -> PrivacyGuardianState:
    """
    Context Compaction Reducer:
    Wipes heavy intermediate DOMs, unparsed raw strings, and sub-agent scratchpad memory
    to isolate sub-agent memory and prevent token bloat across the graph.
    """
    # 1. Clear temporary execution scratchpad
    if state.node_scratchpad:
        logger.debug(f"[Compaction] Wiping node_scratchpad keys: {list(state.node_scratchpad.keys())}")
        state.node_scratchpad.clear()

    # 2. Strip raw document texts while preserving metadata & hash signatures
    for doc in state.site_profile.discovered_policies:
        if doc.content is not None:
            logger.debug(f"[Compaction] Purging raw text content for policy: {doc.url}")
            doc.content = None

    return state