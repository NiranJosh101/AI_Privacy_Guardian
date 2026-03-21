from typing import Dict, Any
from app.agent.state import ExplorerState
from app.mcp.client import MCPClient

async def validation_node(state: ExplorerState) -> Dict[str, Any]:
    """
    The Gatekeeper. Checks if the URL is healthy and accessible 
    before we start the expensive discovery and extraction process.
    """
    client = MCPClient()
    
    try:
        await client.connect()
        
        # Calling the robust validator we built in mcp/tools/validator.py
        result = await client.call_tool(
            "validate_site_access", 
            {"url": state["base_url"]}
        )
        
        # If the validator says we can't proceed, we mark it in the state
        if not result.get("can_proceed", False):
            return {
                "is_blocked": True,
                "error_log": [f"Site Validation Failed: {result.get('error', 'Unknown Error')}"]
            }

        # If it's a redirect, we update the base_url so the Scout starts at the right place
        return {
            "base_url": result.get("final_url", state["base_url"]),
            "is_blocked": False,
            "current_step": "validated"
        }

    except Exception as e:
        return {"is_blocked": True, "error_log": [f"Validator Node Error: {str(e)}"]}
    finally:
        await client.disconnect()