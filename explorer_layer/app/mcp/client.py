import asyncio
import logging
from typing import Optional, Any, Dict
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


class MCPClient:
    """
    The 'Hand' that reaches into the Toolbox (MCP Server).
    Fixed: Properly returns full MCP response instead of just content.
    """

    def __init__(self, url: str = "http://localhost:8008/sse"):
        self.url = url
        self.session: Optional[ClientSession] = None
        self._exit_stack = AsyncExitStack()

    async def connect(self):
        """Initialize SSE connection and MCP session."""
        try:
            logger.debug(f"Connecting to MCP Server at {self.url}")

            streams = await self._exit_stack.enter_async_context(
                sse_client(self.url)
            )
            read_stream, write_stream = streams

            self.session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            await self.session.initialize()
            logger.debug("MCP Handshake Complete")

        except Exception as e:
            await self.disconnect()
            logger.exception(f"Connection Failed: {e}")
            raise


    async def get_available_tools(self):
        if not self.session:
            raise RuntimeError("MCP Client not connected.")

        result = await self.session.list_tools()
        return result.tools


    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if not self.session:
            raise RuntimeError("MCP Client not connected.")

        try:
            logger.debug(f"Calling tool: {tool_name} with args: {arguments}")
            
            # This returns a CallToolResult object
            result = await self.session.call_tool(tool_name, arguments)

            # Check if the tool reported an internal failure
            if hasattr(result, "isError") and result.isError:
                logger.error(f"MCP Tool '{tool_name}' reported an internal error: {result.content}")
            
            # Log the content type for your own sanity during the [TextContent] bug
            content = getattr(result, 'content', [])
            if content:
                logger.debug(f"Content Type: {type(content)}")

            return result

        except Exception as e:
            logger.exception(f"Transport-level failure calling {tool_name}: {e}")
            raise


    async def disconnect(self):
        """Gracefully shut down connection."""
        logger.debug("Disconnecting MCP Client")

        try:
            await self._exit_stack.aclose()
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

        self.session = None