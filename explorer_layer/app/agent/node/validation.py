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
        response = await client.call_tool(
            "validate_site_access", 
            {"url": state["base_url"]}
        )
        
        # 2. Extract content list
        content_list = getattr(response, 'content', response)

        if not content_list or not isinstance(content_list, list):
            raise ValueError(f"Invalid MCP response format: {type(content_list)}")

        # ✅ FIX 1: Correctly grab first item
        first_item = content_list[0]

        # Debug (optional but useful)
        print(f"--- DEBUG: first_item type: {type(first_item)} ---")
        print(f"--- DEBUG: first_item raw: {first_item} ---")

        # 3. Normalize content into `result` dict
        if isinstance(first_item, dict):
            # ✅ Already parsed — best case
            result = first_item

        elif hasattr(first_item, "text"):
            # MCP TextContent object
            try:
                result = json.loads(first_item.text)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON in TextContent: {first_item.text}")

        elif isinstance(first_item, str):
            # Raw string
            try:
                result = json.loads(first_item)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON string: {first_item}")

        else:
            raise ValueError(f"Unsupported content type: {type(first_item)}")

        print(f"--- DEBUG: Validator Result: {result} ---")
        
        # 4. Decision logic
        if not result.get("can_proceed", False):
            print(f"--- DEBUG: Site is blocked or inaccessible: {state['base_url']} ---")
            return {
                "is_blocked": True,
                "error_log": [
                    f"Site Validation Failed: {result.get('error', 'Blocked or inaccessible')}"
                ]
            }

        # 5. Success
        print(f"--- DEBUG: Validation Successful. Moving to Discovery. ---")
        return {
            "base_url": result.get("final_url", state["base_url"]),
            "is_blocked": False,
            "current_step": "validated"
        }

    except Exception as e:
        print(f"--- DEBUG: Validator Node CRASHED: {str(e)} ---")
        return {
            "is_blocked": True, 
            "error_log": [f"Validator Node Error: {str(e)}"]
        }

    finally:
        await client.disconnect()