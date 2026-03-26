import json
from app.agent.state import ExplorerState
from app.mcp.client import MCPClient
from typing import Dict, Any

async def discovery_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Calls the MCP 'discover_regulatory_links' tool to find potential legal URLs.
    """
    client = MCPClient()
    
    try:
        await client.connect()
        
        # 1. Call the tool
        response = await client.call_tool(
            "discover_regulatory_links", 
            {"url": state["base_url"]}
        )
        
        # 2. Extract the content list from the CallToolResult
        content_list = getattr(response, 'content', response)
        
        if not content_list or not isinstance(content_list, list) or len(content_list) == 0:
             raise ValueError("Discovery tool returned no content")

        # 3. Get the raw text from the first item and parse it
        first_item = content_list
        content_text = first_item.text if hasattr(first_item, 'text') else str(first_item)
        
        # CRITICAL: Parse the string into a DICT before saving to state
        # If your tool returns categorization, this will now be a proper Dictionary
        parsed_map = json.loads(content_text)

        print(f"--- DEBUG: Discovery Found {len(parsed_map)} Categories ---")

        return {
            "regulatory_map": parsed_map, # Now this is a Dict, not a List of objects
            "is_blocked": False
        }
        
    except Exception as e:
        print(f"--- DEBUG: Discovery Node CRASHED: {str(e)} ---")
        return {
            "error_log": [f"Discovery failed: {str(e)}"],
            "is_blocked": True
        }
    finally:
        await client.disconnect()