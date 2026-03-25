import json
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
        
        # 1. Call the tool
        raw_result = await client.call_tool(
            "validate_site_access", 
            {"url": state["base_url"]}
        )
        
        # 2. MCP returns a list of content objects. We need the first one's text.
        # Then we parse that string back into a Python dictionary.
        result = json.loads(raw_result.text)
        
        print(f"--- DEBUG: Validator Result: {result} ---")
        
        # 3. Check 'can_proceed' from the parsed tool output
        if not result.get("can_proceed", False):
            print(f"--- DEBUG: Site is blocked or inaccessible: {state['base_url']} ---")
            return {
                "is_blocked": True,
                "error_log": [f"Site Validation Failed: {result.get('error', 'Blocked by site policy or technical error')}"]
            }

        # 4. Successful validation
        print(f"--- DEBUG: Validation Successful. Moving to Discovery. ---")
        return {
            "base_url": result.get("final_url", state["base_url"]),
            "is_blocked": False,
            "current_step": "validated"
        }

    except Exception as e:
        print(f"--- DEBUG: Validator Node CRASHED: {str(e)} ---")
        return {"is_blocked": True, "error_log": [f"Validator Node Error: {str(e)}"]}
    finally:
        await client.disconnect()