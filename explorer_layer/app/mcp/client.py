import asyncio
import sys
from typing import Optional, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """
    The 'Hand' that reaches into the Toolbox (MCP Server).
    This client manages the connection to the ExplorerTools server.
    """
    
    def __init__(self):
        # Point this to your server entry point
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.mcp.server"], 
            env=None
        )
        self.session: Optional[ClientSession] = None
        self._client_context = None

    async def connect(self):
        """Initializes the stdio connection to the MCP server."""
        self._client_context = stdio_client(self.server_params)
        read, write = await self._client_context.__aenter__()
        self.session = ClientSession(read, write)
        await self.session.initialize()

    async def get_available_tools(self):
        """Queries the server to see what tools are registered."""
        if not self.session:
            raise RuntimeError("MCP Client not connected. Call connect() first.")
        return await self.session.list_tools()

    async def call_tool(self, tool_name: str, arguments: dict):
        """Executes a specific tool on the server."""
        if not self.session:
            raise RuntimeError("MCP Client not connected.")
        
        result = await self.session.call_tool(tool_name, arguments)
        return result.content

    async def disconnect(self):
        """Gracefully shuts down the connection and the server subprocess."""
        if self._client_context:
            await self._client_context.__aexit__(None, None, None)

# Usage Example for the LangGraph Node:
# client = MCPClient()
# await client.connect()
# result = await client.call_tool("validate_site_access", {"url": "..."})