from app.agent.state import ExplorerState
from app.mcp.client import MCPClient
from typing import Dict, Any

async def discovery_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Calls the MCP 'scout_links' tool to find potential legal URLs.
    """
    client = MCPClient()
    
    try:
        # Connect to the MCP Server sidecar
        await client.connect()
        
        # Call the LinkScout tool (defined in our mcp/server.py)
        # It returns a Dict[str, List[Dict]] (the categorized candidates)
        raw_suite = await client.call_tool(
            "discover_regulatory_links", 
            {"url": state["base_url"]}
        )
        
        return {
            "regulatory_map": raw_suite,
            "is_blocked": False
        }
        
    except Exception as e:
        return {
            "error_log": [f"Discovery failed: {str(e)}"],
            "is_blocked": True
        }
    finally:
        # Always disconnect to kill the subprocess and free memory
        await client.disconnect()