#!/bin/bash

# 1. Start the MCP server in the background
echo "🚀 Starting MCP Server (app.mcp.server)..."
python -m app.mcp.server --port 8001 & 

# 2. Give the MCP server a few seconds to warm up
sleep 5

# 3. Start the Explorer service in the foreground
# Using 'exec' ensures signals (like SIGTERM) are passed to the python process
echo "🚀 Starting Explorer Service (main.py)..."
exec python main.py