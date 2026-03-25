import asyncio
from typing import Optional, Any, Dict
from contextlib import AsyncExitStack

# Standard MCP imports
from mcp import ClientSession
from mcp.client.sse import sse_client

class MCPClient:
    """
    The 'Hand' that reaches into the Toolbox (MCP Server).
    Refactored for SSE transport and stable context management.
    """
    
    def __init__(self, url: str = "http://localhost:8002/sse"):
        self.url = url
        self.session: Optional[ClientSession] = None
        self._exit_stack = AsyncExitStack()

    async def connect(self):
        """
        Initializes the SSE connection. 
        Using AsyncExitStack ensures background listener tasks start correctly.
        """
        try:
            print(f"--- DEBUG: Connecting to MCP Server at {self.url} ---")
            
            # 1. Connect to the SSE stream
            streams = await self._exit_stack.enter_async_context(sse_client(self.url))
            read_stream, write_stream = streams
            
            # 2. Create the MCP Session
            self.session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # 3. Perform the mandatory JSON-RPC handshake
            await self.session.initialize()
            print("--- DEBUG: MCP Handshake Complete ---")
            
        except Exception as e:
            await self.disconnect()
            print(f"--- DEBUG: Connection Failed: {e} ---")
            raise

    async def get_available_tools(self):
        """Queries the server for registered tools."""
        if not self.session:
            raise RuntimeError("MCP Client not connected. Call connect() first.")
        
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Executes a specific tool on the server and returns the content."""
        if not self.session:
            raise RuntimeError("MCP Client not connected.")
        
        print(f"--- DEBUG: Calling tool: {tool_name} ---")
        result = await self.session.call_tool(tool_name, arguments)
        
        # result.content is usually a list of TextContent/ImageContent objects
        return result.content

    async def disconnect(self):
        """Gracefully shuts down the SSE connection and clears the stack."""
        print("--- DEBUG: Disconnecting MCP Client ---")
        await self._exit_stack.aclose()
        self.session = None

